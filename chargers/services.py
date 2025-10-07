from .repositories import (
    ChargerRepository,
    ConnectorRepository,
    EventLogRepository,
    TransactionRepository,
)


class ChargerService:
    """Business logic for charger lifecycle and state updates."""
    async def on_connected(
        self, charger_id: str, vendor: str | None, model: str | None
    ):
        """Persist charger connection info and log BootNotification."""
        charger = await ChargerRepository.upsert(charger_id, vendor, model)
        await EventLogRepository.log(
            charger_id, "BootNotification", f"Vendor={vendor}, Model={model}"
        )
        return charger

    async def on_heartbeat(self, charger_id: str):
        """Record the latest heartbeat timestamp and log the event."""
        await ChargerRepository.set_heartbeat(charger_id)
        await EventLogRepository.log(charger_id, "Heartbeat", "Received heartbeat")

    async def set_status(self, charger_id: str, status: str):
        """Set charger availability/health status."""
        await ChargerRepository.set_status(charger_id, status)


class TransactionService:
    """Business logic for starting and stopping transactions."""
    async def start(
        self, charger_id: str, connector_id: int, id_tag: str, meter_start: int
    ):
        """Create a new transaction and log StartTransaction."""
        tx = await TransactionRepository.start(
            charger_id, connector_id, id_tag, meter_start
        )
        await EventLogRepository.log(
            charger_id, "StartTransaction", f"tx={tx.transaction_id}"
        )
        return tx

    async def stop(self, transaction_id: int, charger_id: str, meter_stop: int | None):
        """Finalize a transaction and log StopTransaction."""
        tx = await TransactionRepository.stop(transaction_id, meter_stop)
        await EventLogRepository.log(
            charger_id, "StopTransaction", f"tx={tx.transaction_id}"
        )
        return tx
