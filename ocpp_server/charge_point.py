import datetime as dt
from ocpp.routing import on
from ocpp.v16 import call, call_result
from ocpp.v16 import ChargePoint as BaseChargePoint
from chargers.services import ChargerService, TransactionService

class CentralSystemCP(BaseChargePoint):
    def __init__(self, charge_point_id, connection):
        super().__init__(charge_point_id, connection)
        self.charger_service = ChargerService()
        self.tx_service = TransactionService()

    @on("BootNotification")
    async def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        await self.charger_service.on_connected(self.id, charge_point_vendor, charge_point_model)
        now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()
        return call_result.BootNotificationPayload(
            current_time=now,
            interval=10,
            status="Accepted",
        )

    @on("Heartbeat")
    async def on_heartbeat(self):
        await self.charger_service.on_heartbeat(self.id)
        now = dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()
        return call_result.HeartbeatPayload(current_time=now)

    @on("Authorize")
    async def on_authorize(self, id_tag, **kwargs):
        # For demo: accept all
        return call_result.AuthorizePayload(id_tag_info={"status": "Accepted"})

    @on("StartTransaction")
    async def on_start_transaction(self, id_tag, connector_id, meter_start, **kwargs):
        tx = await self.tx_service.start(self.id, connector_id, id_tag, meter_start)
        return call_result.StartTransactionPayload(
            transaction_id=tx.transaction_id,
            id_tag_info={"status": "Accepted"},
        )

    @on("StopTransaction")
    async def on_stop_transaction(self, transaction_id, meter_stop=None, **kwargs):
        await self.tx_service.stop(transaction_id, self.id, meter_stop)
        return call_result.StopTransactionPayload(id_tag_info={"status": "Accepted"})

    async def remote_start(self, id_tag: str):
        req = call.RemoteStartTransactionPayload(id_tag=id_tag)
        return await self.call(req)

    async def remote_stop(self, transaction_id: int):
        req = call.RemoteStopTransactionPayload(transaction_id=transaction_id)
        return await self.call(req)


    @on("StatusNotification")
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        # Log status updates
        print(f"StatusNotification: CP {self.id}, connector {connector_id}, status={status}")
        return call_result.StatusNotificationPayload()

    @on("MeterValues")
    async def on_meter_values(self, connector_id, meter_value, **kwargs):
        print(f"MeterValues: CP {self.id}, connector {connector_id}, meter={meter_value}")
        return call_result.MeterValuesPayload()
