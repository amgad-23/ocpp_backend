import pytest
from chargers.services import ChargerService, TransactionService
from chargers.models import Charger, TransactionStatusChoices

@pytest.mark.django_db
def test_charger_service_boot_and_heartbeat():
    cs = ChargerService()
    c = cs.on_connected("EVSE-20", "VendorX", "ModelY")
    assert c.vendor == "VendorX"
    cs.on_heartbeat("EVSE-20")
    assert Charger.objects.get(id="EVSE-20").last_heartbeat is not None

@pytest.mark.django_db
def test_transaction_service_start_and_stop():
    cs = ChargerService()
    ts = TransactionService()
    cs.on_connected("EVSE-21", "VendorX", "ModelY")
    tx = ts.start("EVSE-21", 1, "RFID-21", 100)
    assert tx.status == TransactionStatusChoices.ACTIVE
    stopped = ts.stop(tx.transaction_id, "EVSE-21", 200)
    assert stopped.status == TransactionStatusChoices.STOPPED
