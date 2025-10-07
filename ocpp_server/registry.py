"""Thread-safe in-memory registry for active charge point connections.

This module allows the WebSocket server and HTTP API to share visibility over
currently connected charge points by id. Access is guarded with an `RLock`
to ensure safety when accessed from multiple threads.
"""

from threading import RLock
from typing import Dict, Optional

_active: Dict[str, object] = {}
_lock = RLock()


def register_cp(charge_point_id: str, cp_obj: object):
    """Register a connected charge point in the active registry.

    Args:
        charge_point_id: The unique OCPP chargePointId.
        cp_obj: The `CentralSystemCP` instance managing the connection.
    """
    with _lock:
        _active[charge_point_id] = cp_obj


def unregister_cp(charge_point_id: str):
    """Remove a charge point from the active registry if present."""
    with _lock:
        _active.pop(charge_point_id, None)


def get_cp(charge_point_id: str) -> Optional[object]:
    """Return the registered `CentralSystemCP` for a charger, if any."""
    with _lock:
        return _active.get(charge_point_id)


def list_cps() -> list[str]:
    """List all active charge point ids currently registered."""
    with _lock:
        return list(_active.keys())
