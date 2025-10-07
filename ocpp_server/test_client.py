import asyncio
import websockets
from ocpp.v16 import ChargePoint as CP, call

class TestChargePoint(CP):
    async def send_boot_notification(self):
        req = call.BootNotification(
            charge_point_model="DemoModel",
            charge_point_vendor="DemoVendor"
        )
        response = await self.call(req)
        print("BootNotification Response:", response)

async def main():
    uri = "ws://localhost:9000/EVSE-002"
    async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
        cp = TestChargePoint("EVSE-002", ws)
        asyncio.create_task(cp.start())
        await cp.send_boot_notification()
        await asyncio.Future()

asyncio.run(main())
