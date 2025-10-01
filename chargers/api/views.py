import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from chargers.models import Charger, Transaction, EventLog
from .serializers import (
    ChargerSerializer, TransactionSerializer, EventLogSerializer
)
from ocpp_server.registry import get_cp, list_cps
from ocpp.v16 import call as ocpp_call


@swagger_auto_schema(
    method="get",
    operation_description="List all registered chargers",
    responses={200: ChargerSerializer(many=True)}
)
@api_view(["GET"])
def list_chargers(request):
    qs = Charger.objects.order_by("id")
    return Response(ChargerSerializer(qs, many=True).data)


@swagger_auto_schema(
    method="get",
    operation_description="List recent transactions (last 200)",
    responses={200: TransactionSerializer(many=True)}
)
@api_view(["GET"])
def list_transactions(request):
    qs = Transaction.objects.order_by("-start_time")[:200]
    return Response(TransactionSerializer(qs, many=True).data)


@swagger_auto_schema(
    method="get",
    operation_description="List recent charger event logs",
    responses={200: EventLogSerializer(many=True)}
)
@api_view(["GET"])
def list_logs(request):
    qs = EventLog.objects.order_by("-created_at")[:200]
    return Response(EventLogSerializer(qs, many=True).data)

start_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "id_tag": openapi.Schema(type=openapi.TYPE_STRING, description="RFID tag"),
    },
    required=["id_tag"]
)

@swagger_auto_schema(
    operation_description="Send RemoteStartTransaction to a charger",
    request_body=start_request_body,
    responses={
        200: openapi.Response("OCPP RemoteStart response"),
        404: "Charger not connected",
    }
)
@csrf_exempt
@permission_classes([IsAuthenticated])   # Require JWT auth
async def remote_start(request, charger_id: str):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    cp = get_cp(charger_id)
    if cp is None:
        return JsonResponse({"error": "Charger not connected"}, status=404)

    body = json.loads(request.body.decode("utf-8")) if request.body else {}
    id_tag = body.get("id_tag", "DEMO123")

    payload = ocpp_call.RemoteStartTransactionPayload(id_tag=id_tag)
    try:
        response = await cp.call(payload)   # ✅ Await OCPP response
        return JsonResponse({"status": "ok", "response": response.__dict__})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ✅ Async Remote Stop
stop_request_body = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        "transaction_id": openapi.Schema(type=openapi.TYPE_INTEGER, description="Transaction ID"),
    },
    required=["transaction_id"]
)

@swagger_auto_schema(
    operation_description="Send RemoteStopTransaction to a charger",
    request_body=stop_request_body,
    responses={
        200: openapi.Response("OCPP RemoteStop response"),
        404: "Charger not connected",
    }
)
@csrf_exempt
@permission_classes([IsAuthenticated])   # Require JWT auth
async def remote_stop(request, charger_id: str):
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    cp = get_cp(charger_id)
    if cp is None:
        return JsonResponse({"error": "Charger not connected"}, status=404)

    body = json.loads(request.body.decode("utf-8")) if request.body else {}
    tx_id = body.get("transaction_id")
    if not tx_id:
        return JsonResponse({"error": "transaction_id required"}, status=400)

    payload = ocpp_call.RemoteStopTransactionPayload(transaction_id=int(tx_id))
    try:
        response = await cp.call(payload)   # ✅ Await OCPP response
        return JsonResponse({"status": "ok", "response": response.__dict__})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

@swagger_auto_schema(
    method="get",
    operation_description="List currently connected chargers (in-memory registry)",
    responses={200: openapi.Response("List of active chargers", schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            "active_chargers": openapi.Schema(
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING)
            )
        }
    ))}
)
@api_view(["GET"])
def list_active_chargers(request):
    """Return currently connected chargers from the in-memory registry."""
    return Response({"active_chargers": list_cps()})


def dashboard(request):
    """Simple dashboard showing chargers and recent transactions."""
    return render(request, "dashboard.html", {
        "chargers": Charger.objects.all(),
        "transactions": Transaction.objects.order_by("-start_time")[:10]
    })