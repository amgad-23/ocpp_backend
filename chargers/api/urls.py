"""URL routes for charger APIs and OCPP remote commands."""

from django.urls import path

from . import views

urlpatterns = [
    # Read-only listing endpoints
    path("chargers/", views.list_chargers, name="list_chargers"),  # List all chargers from DB
    path("chargers/active/", views.list_active_chargers, name="list_active_chargers"),  # List currently connected chargers (in-memory registry)
    path("transactions/", views.list_transactions, name="list_transactions"),  # List recent transactions
    path("logs/", views.list_logs, name="list_logs"),  # List recent charger event logs

    # Remote OCPP commands
    path("chargers/<str:charger_id>/start/", views.remote_start, name="remote_start"),  # Send RemoteStartTransaction to a charger
    path("chargers/<str:charger_id>/stop/", views.remote_stop, name="remote_stop"),  # Send RemoteStopTransaction to a charger
    path("chargers/<str:charger_id>/trigger/heartbeat/", views.trigger_heartbeat, name="trigger_heartbeat"),  # Trigger Heartbeat via OCPP

    # Proxy routes to OCPP HTTP API
    path(
        "ocpp-control/<str:charger_id>/start/",
        views.OcppProxyStartView.as_view(),
        name="ocpp_proxy_start",
    ),
    path(
        "ocpp-control/<str:charger_id>/stop/",
        views.OcppProxyStopView.as_view(),
        name="ocpp_proxy_stop",
    ),
    path(
        "ocpp-control/<str:charger_id>/trigger/heartbeat/",
        views.OcppProxyTriggerHBView.as_view(),
        name="ocpp_proxy_trigger_hb",
    ),

    # Demo transaction helpers (no OCPP call)
    path(
        "chargers/<str:charger_id>/demo/start/",
        views.demo_start_transaction,
        name="demo_start_transaction",
    ),
    path(
        "chargers/<str:charger_id>/demo/stop/",
        views.demo_stop_transaction,
        name="demo_stop_transaction",
    ),
]
