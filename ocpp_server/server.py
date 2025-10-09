"""OCPP 1.6 WebSocket server entrypoint.

Exposes an async server that accepts multiple concurrent charge point
connections. Each new connection is wrapped in a `CentralSystemCP` instance
and registered in the in-memory registry for later lookup by the HTTP API.
"""

import asyncio
import os

import websockets
import uvicorn

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
    """Start the OCPP WebSocket server and the HTTP control API."""
    # Start FastAPI (HTTP control API) alongside the websocket server
    http_host = os.getenv("OCPP_HTTP_HOST", "0.0.0.0")
    http_port = int(os.getenv("OCPP_HTTP_PORT", 9100))
    config = uvicorn.Config(
        "ocpp_server.http_api:app",
        host=http_host,
        port=http_port,
        log_level="info",
        lifespan="off",
    )
    http_server = uvicorn.Server(config)

    async with websockets.serve(
        on_connect,
        host=HOST,
        port=PORT,
        subprotocols=["ocpp1.6"],
        ping_interval=60,
        ping_timeout=60,
    ):
        print(f"OCPP 1.6 server running at ws://{HOST}:{PORT}")
        print(f"OCPP HTTP API running at http://{http_host}:{http_port}")
        await http_server.serve()


if __name__ == "__main__":
    asyncio.run(main())
