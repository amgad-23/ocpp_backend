import asyncio
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from ocpp.v16 import call as ocpp_call
from ocpp.v16.enums import MessageTrigger

from .registry import get_cp, list_cps


class StartBody(BaseModel):
    id_tag: str


class StopBody(BaseModel):
    transaction_id: int


app = FastAPI(title="OCPP Control API", version="1.0.0")


@app.get("/api/chargers/active/")
async def active():
    return {"active_chargers": list_cps()}


@app.post("/api/chargers/{charger_id}/start/")
async def remote_start(charger_id: str, body: StartBody):
    cp = get_cp(charger_id)
    if cp is None:
        raise HTTPException(status_code=404, detail="Charger not connected")
    payload = ocpp_call.RemoteStartTransaction(id_tag=body.id_tag)
    try:
        # Avoid hanging indefinitely if a stale CP is registered
        resp = await asyncio.wait_for(cp.call(payload), timeout=5.0)
        return {"status": "ok", "response": getattr(resp, "__dict__", {})}
    except Exception as e:
        if isinstance(e, asyncio.TimeoutError):
            raise HTTPException(status_code=504, detail="OCPP call timed out")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chargers/{charger_id}/stop/")
async def remote_stop(charger_id: str, body: StopBody):
    cp = get_cp(charger_id)
    if cp is None:
        raise HTTPException(status_code=404, detail="Charger not connected")
    payload = ocpp_call.RemoteStopTransaction(transaction_id=body.transaction_id)
    try:
        resp = await asyncio.wait_for(cp.call(payload), timeout=5.0)
        return {"status": "ok", "response": getattr(resp, "__dict__", {})}
    except Exception as e:
        if isinstance(e, asyncio.TimeoutError):
            raise HTTPException(status_code=504, detail="OCPP call timed out")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chargers/{charger_id}/trigger/heartbeat/")
async def trigger_hb(charger_id: str):
    cp = get_cp(charger_id)
    if cp is None:
        raise HTTPException(status_code=404, detail="Charger not connected")
    try:
        payload = ocpp_call.TriggerMessage(requested_message=MessageTrigger.Heartbeat)
        resp = await asyncio.wait_for(cp.call(payload), timeout=5.0)
        return {"status": "ok", "response": getattr(resp, "__dict__", {})}
    except Exception as e:
        if isinstance(e, asyncio.TimeoutError):
            raise HTTPException(status_code=504, detail="OCPP call timed out")
        # Be lenient: many CPs send the Heartbeat even if the TriggerMessage response is odd
        return {"status": "ok", "note": "Triggered Heartbeat (with warning)", "detail": str(e)}
