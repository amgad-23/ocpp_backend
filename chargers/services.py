from .repositories import (ChargerRepository, TransactionRepository, EventLogRepository, ConnectorRepository)


class ChargerService:
    async def on_connected(self, charger_id: str, vendor: str | None, model: str | None):
        charger = await ChargerRepository.upsert(charger_id, vendor, model)
        await EventLogRepository.log(charger_id, "BootNotification", f"Vendor={vendor}, Model={model}")
        return charger

    async def on_heartbeat(self, charger_id: str):
        await ChargerRepository.set_heartbeat(charger_id)
        await EventLogRepository.log(charger_id, "Heartbeat", "Received heartbeat")

    async def set_status(self, charger_id: str, status: str):
        await ChargerRepository.set_status(charger_id, status)


class TransactionService:
    async def start(self, charger_id: str, connector_id: int, id_tag: str, meter_start: int):
        tx = await TransactionRepository.start(charger_id, connector_id, id_tag, meter_start)
        await EventLogRepository.log(charger_id, "StartTransaction", f"tx={tx.transaction_id}")
        return tx

    async def stop(self, transaction_id: int, charger_id: str, meter_stop: int | None):
        tx = await TransactionRepository.stop(transaction_id, meter_stop)
        await EventLogRepository.log(charger_id, "StopTransaction", f"tx={tx.transaction_id}")
        return tx

