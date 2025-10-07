import datetime as dt

from ocpp.routing import on
from ocpp.v16 import ChargePoint as BaseChargePoint
from ocpp.v16 import call, call_result
from ocpp.v16.datatypes import IdTagInfo
from ocpp.v16.enums import RegistrationStatus, AuthorizationStatus

from chargers.services import ChargerService, TransactionService


class CentralSystemCP(BaseChargePoint):
    """Central system representation of a connected charge point.

    Provides async OCPP 1.6 handlers for core messages and exposes helpers to
    initiate remote commands. Delegates persistence and business logic to the
    services layer.
    """
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.charger_service = ChargerService()
        self.tx_service = TransactionService()

    @on("BootNotification")
    async def on_boot_notification(
        self, charge_point_model, charge_point_vendor, **kwargs
    ):
        """Handle BootNotification; persist charger details and accept.

        Persists vendor/model, logs event, and returns Accepted with current
        time and heartbeat interval.
        """
        await self.charger_service.on_connected(
            self.id, charge_point_vendor, charge_point_model
        )
        now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()
        return call_result.BootNotification(
            current_time=now,
            interval=10,
            status= RegistrationStatus.accepted,
        )

    @on("Heartbeat")
    async def on_heartbeat(self):
        """Handle Heartbeat; update last heartbeat and echo current time."""
        await self.charger_service.on_heartbeat(self.id)
        now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()
        return call_result.Heartbeat(current_time=now)

    @on("Authorize")
    async def on_authorize(self, id_tag, **kwargs):
        """Handle Authorize; accept all tags (demo implementation)."""
        return call_result.Authorize(id_tag_info=IdTagInfo(status=AuthorizationStatus.accepted))

    @on("StartTransaction")
    async def on_start_transaction(self, id_tag, connector_id, meter_start, **kwargs):
        """Handle StartTransaction; create transaction and accept."""
        tx = await self.tx_service.start(self.id, connector_id, id_tag, meter_start)
        return call_result.StartTransaction(
            transaction_id=tx.transaction_id,
            id_tag_info=IdTagInfo(status=AuthorizationStatus.accepted))


    @on("StopTransaction")
    async def on_stop_transaction(self, transaction_id, meter_stop=None, **kwargs):
        """Handle StopTransaction; finalize transaction and accept."""
        await self.tx_service.stop(transaction_id, self.id, meter_stop)
        return call_result.StopTransaction(id_tag_info=IdTagInfo(status=AuthorizationStatus.accepted))

    async def remote_start(self, id_tag: str):
        """Send RemoteStartTransaction to the CP and return its response."""
        req = call.RemoteStartTransaction(id_tag=id_tag)
        return await self.call(req)

    async def remote_stop(self, transaction_id: int):
        """Send RemoteStopTransaction to the CP and return its response."""
        req = call.RemoteStopTransaction(transaction_id=transaction_id)
        return await self.call(req)

    @on("StatusNotification")
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        """Handle StatusNotification; log basic state changes (demo)."""
        print(
            f"StatusNotification: CP {self.id}, connector {connector_id}, status={status}"
        )
        return call_result.StatusNotification()

    @on("MeterValues")
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        """Handle MeterValues; log incoming telemetry (demo)."""
        print(
            f"MeterValues: CP {self.id}, connector {connector_id}, meter={meter_value}"
        )
        return call_result.MeterValues()
