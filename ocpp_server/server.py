import asyncio
import os
import websockets

# Initialize Django
from .app_django import *  # noqa

from .registry import register_cp, unregister_cp
from .charge_point import CentralSystemCP

HOST = os.getenv("OCPP_WS_HOST", "0.0.0.0")
PORT = int(os.getenv("OCPP_WS_PORT", 9000))

async def on_connect(websocket, path):
    charge_point_id = path.strip("/") or "unknown-cp"
    cp = CentralSystemCP(charge_point_id, websocket)
    register_cp(charge_point_id, cp)
    try:
        await cp.start()
    finally:
        unregister_cp(charge_point_id)

async def main():
    async with websockets.serve(
        on_connect, host=HOST, port=PORT, subprotocols=["ocpp1.6"]
    ):
        print(f"OCPP 1.6 server running at ws://{HOST}:{PORT}")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
