from django.contrib import admin

from .models import Charger, EventLog, Transaction


@admin.register(Charger)
class ChargerAdmin(admin.ModelAdmin):
    list_display = ("id", "vendor", "model", "status", "last_heartbeat", "connected_at")
    search_fields = ("id", "vendor", "model")


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        "transaction_id",
        "charger",
        "connector_id",
        "id_tag",
        "status",
        "start_time",
        "stop_time",
    )
    search_fields = ("id_tag",)


@admin.register(EventLog)
class EventLogAdmin(admin.ModelAdmin):
    list_display = ("charger", "event", "message", "created_at")
    search_fields = ("event", "message")
