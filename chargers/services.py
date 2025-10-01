from .repositories import (ChargerRepository, TransactionRepository, EventLogRepository, ConnectorRepository)


class ChargerService:
    def on_connected(self, charger_id: str, vendor: str | None, model: str | None):
        charger = ChargerRepository.upsert(charger_id, vendor, model)
        EventLogRepository.log(charger_id, "BootNotification", f"Vendor={vendor}, Model={model}")
        return charger


    def on_heartbeat(self, charger_id: str):
        ChargerRepository.set_heartbeat(charger_id)
        EventLogRepository.log(charger_id, "Heartbeat", "Received heartbeat")


    def set_status(self, charger_id: str, status: str):
        ChargerRepository.set_status(charger_id, status)


class TransactionService:
    def start(self, charger_id: str, connector_id: int, id_tag: str, meter_start: int):
        tx = TransactionRepository.start(charger_id, connector_id, id_tag, meter_start)
        EventLogRepository.log(charger_id, "StartTransaction", f"tx={tx.transaction_id}")
        return tx


    def stop(self, transaction_id: int, charger_id: str, meter_stop: int | None):
        tx = TransactionRepository.stop(transaction_id, meter_stop)
        EventLogRepository.log(charger_id, "StopTransaction", f"tx={tx.transaction_id}")
        return tx

