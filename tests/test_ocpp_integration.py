import asyncio

import pytest
import websockets
from ocpp.v16 import ChargePoint as CP
from ocpp.v16 import call


class DummyCP(CP):
    async def start_boot(self):
        req = call.BootNotificationPayload(
            charge_point_model="TestModel", charge_point_vendor="TestVendor"
        )
        return await self.call(req)


@pytest.mark.asyncio
async def test_bootnotification_integration():
    uri = "ws://localhost:9000/EVSE-TEST"
    async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
        cp = DummyCP("EVSE-TEST", ws)
        asyncio.create_task(cp.start())
        resp = await cp.start_boot()
        assert resp["status"] == "Accepted"
