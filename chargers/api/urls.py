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
]
