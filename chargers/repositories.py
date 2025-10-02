from django.utils import timezone
from asgiref.sync import sync_to_async
from .models import (Charger, Transaction, EventLog, StatusChoices, Connector, ConnectorTransaction, ConnectorTransactionStatusChoices, TransactionStatusChoices)


class ChargerRepository:
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
        return Charger.objects.filter(id=charger_id).update(last_heartbeat=timezone.now())


class TransactionRepository:
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


class EventLogRepository:
    @staticmethod
    @sync_to_async
    def log(charger_id: str, event: str, message: str):
        charger = Charger.objects.get(id=charger_id)
        return EventLog.objects.create(charger=charger, event=event, message=message)


class ConnectorRepository:
    @staticmethod
    @sync_to_async
    def upsert(charger_id: str, connector_id: int):
        obj, _ = Connector.objects.get_or_create(charger_id=charger_id, connector_id=connector_id)
        return obj

