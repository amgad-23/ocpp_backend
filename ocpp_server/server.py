"""OCPP 1.6 WebSocket server entrypoint.

Exposes an async server that accepts multiple concurrent charge point
connections. Each new connection is wrapped in a `CentralSystemCP` instance
and registered in the in-memory registry for later lookup by the HTTP API.
"""

import asyncio
import os

import websockets

# Initialize Django
from .app_django import *  # noqa
from .charge_point import CentralSystemCP
from .registry import register_cp, unregister_cp

HOST = os.getenv("OCPP_WS_HOST", "0.0.0.0")
PORT = int(os.getenv("OCPP_WS_PORT", 9000))


async def on_connect(websocket):
    path = websocket.request.path if hasattr(websocket, "request") else "/unknown"
    charge_point_id = path.strip("/") or "unknown-cp"

    cp = CentralSystemCP(charge_point_id, websocket)
    register_cp(charge_point_id, cp)
    try:
        await cp.start()
    except Exception as e:
        if "ConnectionClosed" not in str(type(e)):
            print(f"Unexpected error from {charge_point_id}: {e}")
    finally:
        unregister_cp(charge_point_id)


async def main():
    """Start the OCPP WebSocket server and run indefinitely."""
    async with websockets.serve(
            on_connect,
            host=HOST,
            port=PORT,
            subprotocols=["ocpp1.6"],
            ping_interval=60,
            ping_timeout=60,
    ):
        print(f"OCPP 1.6 server running at ws://{HOST}:{PORT}")
        await asyncio.Future()


if __name__ == "__main__":
    asyncio.run(main())
