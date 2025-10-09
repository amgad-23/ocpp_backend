"""REST API endpoints for listing data and sending remote OCPP commands."""

import json
import os

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from ocpp.v16 import call as ocpp_call
from ocpp.v16.enums import MessageTrigger
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from chargers.models import Charger, EventLog, Transaction, TransactionStatusChoices
from chargers.services import TransactionService
from ocpp_server.registry import get_cp, list_cps
import httpx

from .serializers import ChargerSerializer, EventLogSerializer, TransactionSerializer


# --- Internal helper for proxying to the OCPP HTTP service ---
def _ocpp_http_bases() -> list[str]:
    bases: list[str] = []
    env_base = os.getenv("OCPP_HTTP_BASE_URL")
    if env_base:
        bases.append(env_base.rstrip("/"))
    # Prefer Docker service first (container-to-container), then local port, then nginx path
    bases.extend([
        "http://ocpp:9100",           # docker service name (most reliable in compose)
        "http://localhost:9100",      # direct local process (without nginx)
        "http://localhost/ocpp-api",  # nginx reverse proxy path (host context only)
    ])
    # De-duplicate while preserving order
    seen = set()
    out: list[str] = []
    for b in bases:
        if b and b not in seen:
            seen.add(b)
            out.append(b)
    return out


def _proxy_post(path: str, payload: dict) -> httpx.Response:
    # In httpx>=0.28, Timeout must either provide a default or all four fields.
    # Provide a sensible default and override connect/read for snappier behavior.
    timeout = httpx.Timeout(10.0, connect=1.5, read=9.0)
    errors: list[str] = []
    with httpx.Client(timeout=timeout) as client:
        for base in _ocpp_http_bases():
            url = f"{base}{path}"
            try:
                return client.post(url, json=payload)
            except (httpx.ConnectError, httpx.ConnectTimeout, httpx.ReadTimeout) as e:
                errors.append(f"{url} -> {type(e).__name__}")
                continue
    raise httpx.HTTPError("All OCPP endpoints failed: " + "; ".join(errors))


@swagger_auto_schema(
    method="get",
    operation_description="List all registered chargers",
    responses={200: ChargerSerializer(many=True)},
)
@swagger_auto_schema(
    method="post",
    operation_description=(
        "Create or update a charger by id. Useful for pre-provisioning from the dashboard."
    ),
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "id": openapi.Schema(type=openapi.TYPE_STRING, description="Charger ID (<=64)"),
            "vendor": openapi.Schema(type=openapi.TYPE_STRING, description="Vendor name"),
            "model": openapi.Schema(type=openapi.TYPE_STRING, description="Model name"),
        },
        required=["id"],
    ),
    responses={200: ChargerSerializer, 201: ChargerSerializer, 400: "Invalid input", 401: "Unauthorized"},
)
@csrf_exempt
@api_view(["GET", "POST"])
def list_chargers(request):
    """GET: list chargers. POST: create/upsert charger (auth required)."""
    if request.method == "GET":
        qs = Charger.objects.order_by("id")
        return Response(ChargerSerializer(qs, many=True).data)

    # POST create/upsert — accept Django session auth too
    django_user = getattr(getattr(request, "_request", request), "user", None)
    if not (django_user and getattr(django_user, "is_authenticated", False)):
        return JsonResponse({"error": "Authentication required"}, status=401)

    # Use DRF-parsed data only (avoid accessing request.body)
    body = getattr(request, "data", {}) or {}

    charger_id = (body.get("id") or "").strip()
    vendor = (body.get("vendor") or None)
    model = (body.get("model") or None)

    if not charger_id:
        return JsonResponse({"error": "'id' is required"}, status=400)
    if len(charger_id) > 64:
        return JsonResponse({"error": "id must be <= 64 characters"}, status=400)
    # Basic character whitelist: letters, digits, dash, underscore, dot, colon
    import re

    if not re.fullmatch(r"[A-Za-z0-9_.:-]+", charger_id):
        return JsonResponse({"error": "id contains invalid characters"}, status=400)

    obj, created = Charger.objects.get_or_create(id=charger_id)
    if vendor is not None:
        obj.vendor = vendor
    if model is not None:
        obj.model = model
    obj.save()

    data = ChargerSerializer(obj).data
    return JsonResponse(data, status=201 if created else 200)


@swagger_auto_schema(
    method="get",
    operation_description="List recent transactions (last 200)",
    responses={200: TransactionSerializer(many=True)},
)
@api_view(["GET"])
def list_transactions(request):
    """Return the last 200 transactions, newest first."""
    qs = Transaction.objects.order_by("-start_time")[:200]
    return Response(TransactionSerializer(qs, many=True).data)


@swagger_auto_schema(
    method="get",
    operation_description="List recent charger event logs",
    responses={200: EventLogSerializer(many=True)},
)
@api_view(["GET"])
def list_logs(request):
    """Return the last 200 event logs, newest first."""
    qs = EventLog.objects.order_by("-created_at")[:200]
    return Response(EventLogSerializer(qs, many=True).data)


start_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id_tag": openapi.Schema(type=openapi.TYPE_STRING, description="RFID tag"),
    },
    required=["id_tag"],
)


@swagger_auto_schema(
    operation_description="Send RemoteStartTransaction to a charger",
    request_body=start_request_body,
    responses={
        200: openapi.Response("OCPP RemoteStart response"),
        404: "Charger not connected",
    },
)
@csrf_exempt
@permission_classes([IsAuthenticated])  # Require JWT auth
async def remote_start(request, charger_id: str):
    """Send RemoteStartTransaction to a connected charger and return its response."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    cp = get_cp(charger_id)
    if cp is None:
        return JsonResponse({"error": "Charger not connected"}, status=404)

    body = getattr(request, "data", {}) or {}
    id_tag = body.get("id_tag", "DEMO123")

    payload = ocpp_call.RemoteStartTransaction(id_tag=id_tag)
    try:
        response = await cp.call(payload)  # ✅ Await OCPP response
        return JsonResponse({"status": "ok", "response": response.__dict__})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ Async Remote Stop
stop_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "transaction_id": openapi.Schema(
            type=openapi.TYPE_INTEGER, description="Transaction ID"
        ),
    },
    required=["transaction_id"],
)


@swagger_auto_schema(
    operation_description="Send RemoteStopTransaction to a charger",
    request_body=stop_request_body,
    responses={
        200: openapi.Response("OCPP RemoteStop response"),
        404: "Charger not connected",
    },
)
@csrf_exempt
@permission_classes([IsAuthenticated])  # Require JWT auth
async def remote_stop(request, charger_id: str):
    """Send RemoteStopTransaction to a connected charger and return its response."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    cp = get_cp(charger_id)
    if cp is None:
        return JsonResponse({"error": "Charger not connected"}, status=404)

    body = getattr(request, "data", {}) or {}
    tx_id = body.get("transaction_id")
    if not tx_id:
        return JsonResponse({"error": "transaction_id required"}, status=400)

    payload = ocpp_call.RemoteStopTransaction(transaction_id=int(tx_id))
    try:
        response = await cp.call(payload)  # ✅ Await OCPP response
        return JsonResponse({"status": "ok", "response": response.__dict__})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@swagger_auto_schema(
    operation_description="Trigger Heartbeat on a connected charger via OCPP TriggerMessage",
    responses={
        200: openapi.Response("OCPP TriggerMessage(Heartbeat) response"),
        404: "Charger not connected",
    },
)
@csrf_exempt
@permission_classes([IsAuthenticated])
async def trigger_heartbeat(request, charger_id: str):
    """Request a Heartbeat from a connected CP using TriggerMessage.

    If the charger is not connected, returns 404. Requires authentication.
    """
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    cp = get_cp(charger_id)
    if cp is None:
        return JsonResponse({"error": "Charger not connected"}, status=404)

    try:
        payload = ocpp_call.TriggerMessage(requested_message=MessageTrigger.Heartbeat)
        response = await cp.call(payload)
        return JsonResponse({"status": "ok", "response": getattr(response, "__dict__", {})})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@swagger_auto_schema(
    method="get",
    operation_description="List currently connected chargers (in-memory registry)",
    responses={
        200: openapi.Response(
            "List of active chargers",
            schema=openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "active_chargers": openapi.Schema(
                        type=openapi.TYPE_ARRAY,
                        items=openapi.Items(type=openapi.TYPE_STRING),
                    )
                },
            ),
        )
    },
)
@api_view(["GET"])
def list_active_chargers(request):
    """Return currently connected chargers from the in-memory registry."""
    return Response({"active_chargers": list_cps()})


def dashboard(request):
    """Simple dashboard showing chargers and recent transactions."""
    return render(
        request,
        "dashboard.html",
        {
            "chargers": Charger.objects.all(),
            "transactions": Transaction.objects.order_by("-start_time")[:10],
        },
    )


# Proxy endpoints to OCPP HTTP API (avoid cross-process registry issues)
class OcppProxyStartView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Proxy: Send RemoteStartTransaction to a charger via internal OCPP service",
        request_body=start_request_body,
        responses={
            200: openapi.Response("Proxied OCPP RemoteStart response"),
            401: "Unauthorized",
            404: "Charger not connected",
        },
    )
    def post(self, request, charger_id: str):
        body = getattr(request, "data", {}) or {}
        id_tag = body.get("id_tag", "DEMO123")
        try:
            r = _proxy_post(f"/api/chargers/{charger_id}/start/", {"id_tag": id_tag})
            try:
                data = r.json()
            except Exception:
                data = {"error": "Non-JSON response from OCPP API", "body": r.text[:1000]}
            return JsonResponse(data, status=r.status_code)
        except httpx.ReadTimeout as e:
            return JsonResponse({"error": "OCPP service timed out"}, status=504)
        except httpx.HTTPError as e:
            return JsonResponse({"error": str(e)}, status=502)


class OcppProxyStopView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Proxy: Send RemoteStopTransaction to a charger via internal OCPP service",
        request_body=stop_request_body,
        responses={
            200: openapi.Response("Proxied OCPP RemoteStop response"),
            401: "Unauthorized",
            404: "Charger not connected",
        },
    )
    def post(self, request, charger_id: str):
        body = getattr(request, "data", {}) or {}
        tx_id = body.get("transaction_id")
        if not tx_id:
            latest = (
                Transaction.objects.filter(
                    charger_id=charger_id, status=TransactionStatusChoices.ACTIVE
                )
                .order_by("-start_time")
                .first()
            )
            if not latest:
                return JsonResponse({"error": "No active transaction"}, status=404)
            tx_id = latest.transaction_id
        try:
            r = _proxy_post(
                f"/api/chargers/{charger_id}/stop/", {"transaction_id": int(tx_id)}
            )
            try:
                data = r.json()
            except Exception:
                data = {"error": "Non-JSON response from OCPP API", "body": r.text[:1000]}
            return JsonResponse(data, status=r.status_code)
        except httpx.ReadTimeout:
            return JsonResponse({"error": "OCPP service timed out"}, status=504)
        except httpx.HTTPError as e:
            return JsonResponse({"error": str(e)}, status=502)


class OcppProxyTriggerHBView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Proxy: Trigger Heartbeat on a connected charger via internal OCPP service",
        responses={
            200: openapi.Response("Proxied OCPP TriggerMessage(Heartbeat) response"),
            401: "Unauthorized",
            404: "Charger not connected",
        },
    )
    def post(self, request, charger_id: str):
        try:
            r = _proxy_post(
                f"/api/chargers/{charger_id}/trigger/heartbeat/", {}
            )
            try:
                data = r.json()
            except Exception:
                data = {"error": "Non-JSON response from OCPP API", "body": r.text[:1000]}
            return JsonResponse(data, status=r.status_code)
        except httpx.ReadTimeout:
            return JsonResponse({"error": "OCPP service timed out"}, status=504)
        except httpx.HTTPError as e:
            return JsonResponse({"error": str(e)}, status=502)


# --- Demo transaction endpoints (no OCPP required) ---
demo_start_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id_tag": openapi.Schema(type=openapi.TYPE_STRING, description="RFID tag"),
        "connector_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Connector id", default=1),
        "meter_start": openapi.Schema(type=openapi.TYPE_INTEGER, description="Initial meter value", default=0),
    },
)


@swagger_auto_schema(
    method="post",
    operation_description="Demo: create a local Transaction record without contacting a charger",
    request_body=demo_start_request_body,
    responses={201: TransactionSerializer},
)
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
async def demo_start_transaction(request, charger_id: str):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    body = getattr(request, "data", {}) or {}
    id_tag = body.get("id_tag", "DEMO123")
    connector_id = int(body.get("connector_id", 1) or 1)
    meter_start = int(body.get("meter_start", 0) or 0)
    svc = TransactionService()
    try:
        tx = await svc.start(charger_id, connector_id, id_tag, meter_start)
        return JsonResponse(TransactionSerializer(tx).data, status=201)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


demo_stop_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "transaction_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Transaction ID (optional; uses latest if omitted)"),
        "meter_stop": openapi.Schema(type=openapi.TYPE_INTEGER, description="Final meter value", default=100),
    },
)


@swagger_auto_schema(
    method="post",
    operation_description="Demo: stop a local Transaction (uses latest started for the charger if ID omitted)",
    request_body=demo_stop_request_body,
    responses={200: TransactionSerializer, 404: "No active transaction"},
)
@csrf_exempt
@api_view(["POST"])
@permission_classes([IsAuthenticated])
async def demo_stop_transaction(request, charger_id: str):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)
    body = getattr(request, "data", {}) or {}
    tx_id = body.get("transaction_id")
    meter_stop = int(body.get("meter_stop", 100) or 100)
    svc = TransactionService()
    try:
        if not tx_id:
            latest = await svc.latest_started(charger_id)
            if not latest:
                return JsonResponse({"error": "No active transaction"}, status=404)
            tx_id = latest.transaction_id
        tx = await svc.stop(int(tx_id), charger_id, meter_stop)
        return JsonResponse(TransactionSerializer(tx).data, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
