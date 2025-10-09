"""Async-friendly data access layer using Django ORM.

All repository methods wrap synchronous ORM calls with `sync_to_async` so
they can be awaited from async contexts without blocking the event loop.
"""

from asgiref.sync import sync_to_async

from django.utils import timezone

from .models import (
    Charger,
    Connector,
    ConnectorTransaction,
    ConnectorTransactionStatusChoices,
    EventLog,
    StatusChoices,
    Transaction,
    TransactionStatusChoices,
)


class ChargerRepository:
    """CRUD operations for `Charger` with async wrappers."""
    @staticmethod
    @sync_to_async
    def upsert(charger_id: str, vendor: str | None, model: str | None):
        obj, _ = Charger.objects.get_or_create(id=charger_id)
        if vendor is not None:
            obj.vendor = vendor
        if model is not None:
            obj.model = model
            obj.status = StatusChoices.CONNECTED
            obj.connected_at = obj.connected_at or timezone.now()
            obj.save()
        return obj

    @staticmethod
    @sync_to_async
    def set_status(charger_id: str, status: str):
        return Charger.objects.filter(id=charger_id).update(status=status)

    @staticmethod
    @sync_to_async
    def set_heartbeat(charger_id: str):
        return Charger.objects.filter(id=charger_id).update(
            last_heartbeat=timezone.now()
        )


class TransactionRepository:
    """Create/update `Transaction` records via async wrappers."""
    @staticmethod
    @sync_to_async
    def start(charger_id: str, connector_id: int, id_tag: str, meter_start: int):
        charger = Charger.objects.get(id=charger_id)
        tx = Transaction.objects.create(
            charger=charger,
            connector_id=connector_id,
            id_tag=id_tag,
            meter_start=meter_start,
        )
        return tx

    @staticmethod
    @sync_to_async
    def stop(transaction_id: int, meter_stop: int | None):
        tx = Transaction.objects.get(transaction_id=transaction_id)
        tx.meter_stop = meter_stop
        tx.status = TransactionStatusChoices.STOPPED
        tx.stop_time = timezone.now()
        tx.save()
        return tx

    @staticmethod
    @sync_to_async
    def latest_started_for_charger(charger_id: str):
        return (
            Transaction.objects.filter(
                charger_id=charger_id, status=TransactionStatusChoices.ACTIVE
            )
            .order_by("-start_time")
            .first()
        )


class EventLogRepository:
    """Append structured event logs for chargers."""
    @staticmethod
    @sync_to_async
    def log(charger_id: str, event: str, message: str):
        charger = Charger.objects.get(id=charger_id)
        return EventLog.objects.create(charger=charger, event=event, message=message)


class ConnectorRepository:
    """Manage `Connector` records with async wrappers."""
    @staticmethod
    @sync_to_async
    def upsert(charger_id: str, connector_id: int):
        obj, _ = Connector.objects.get_or_create(
            charger_id=charger_id, connector_id=connector_id
        )
        return obj
