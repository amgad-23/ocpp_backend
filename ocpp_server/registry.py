from threading import RLock
from typing import Dict, Optional

_active: Dict[str, object] = {}
_lock = RLock()


def register_cp(charge_point_id: str, cp_obj: object):
    with _lock:
        _active[charge_point_id] = cp_obj


def unregister_cp(charge_point_id: str):
    with _lock:
        _active.pop(charge_point_id, None)


def get_cp(charge_point_id: str) -> Optional[object]:
    with _lock:
        return _active.get(charge_point_id)


def list_cps() -> list[str]:
    with _lock:
        return list(_active.keys())
