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
        print("✅ BootNotification Response:", response)

    async def send_heartbeat(self):
        req = call.Heartbeat()
        response = await self.call(req)
        print("💓 Heartbeat Response:", response)

    async def send_authorize(self):
        id_tag = input("Enter RFID/tag to authorize: ") or "DEMO123"
        req = call.Authorize(id_tag=id_tag)
        response = await self.call(req)
        print("🔑 Authorize Response:", response)

    async def send_start_transaction(self):
        id_tag = input("Enter ID Tag for StartTransaction: ") or "RFID-001"
        connector_id = int(input("Enter connector id (e.g., 1): ") or 1)
        meter_start = int(input("Enter meter start value: ") or 100)
        req = call.StartTransaction(
            connector_id=connector_id,
            id_tag=id_tag,
            meter_start=meter_start,
            timestamp="2025-10-07T12:00:00Z"
        )
        response = await self.call(req)
        print("⚡ StartTransaction Response:", response)

    async def send_stop_transaction(self):
        transaction_id = int(input("Enter transaction id to stop: ") or 1)
        meter_stop = int(input("Enter meter stop value: ") or 150)
        req = call.StopTransaction(
            transaction_id=transaction_id,
            meter_stop=meter_stop,
            timestamp="2025-10-07T12:10:00Z"
        )
        response = await self.call(req)
        print("🛑 StopTransaction Response:", response)


async def main():
    uri = input("Enter WebSocket URI [ws://localhost:9000/EVSE-002]: ") or "ws://localhost:9000/EVSE-002"
    async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
        cp = TestChargePoint("EVSE-002", ws)
        asyncio.create_task(cp.start())

        print("\n🔌 Connected to Central System.\n")
        print("Choose an OCPP action:")
        print("1. BootNotification")
        print("2. Heartbeat")
        print("3. Authorize")
        print("4. StartTransaction")
        print("5. StopTransaction")
        print("6. Exit")

        while True:
            choice = input("\nEnter choice (1–6): ").strip()

            if choice == "1":
                await cp.send_boot_notification()
            elif choice == "2":
                await cp.send_heartbeat()
            elif choice == "3":
                await cp.send_authorize()
            elif choice == "4":
                await cp.send_start_transaction()
            elif choice == "5":
                await cp.send_stop_transaction()
            elif choice == "6":
                print("👋 Exiting client...")
                break
            else:
                print("❌ Invalid choice.")

        print("Disconnecting...")
        await asyncio.sleep(1)

asyncio.run(main())
