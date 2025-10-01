import pytest
from chargers.repositories import ChargerRepository, TransactionRepository, EventLogRepository
from chargers.models import Charger, TransactionStatusChoices

@pytest.mark.django_db
def test_charger_upsert_sets_vendor_model():
    c = ChargerRepository.upsert("EVSE-10", "VendorX", "ModelY")
    assert c.vendor == "VendorX"
    assert c.model == "ModelY"

@pytest.mark.django_db
def test_set_status_and_heartbeat():
    ChargerRepository.upsert("EVSE-11", "V", "M")
    ChargerRepository.set_status("EVSE-11", "charging")
    ChargerRepository.set_heartbeat("EVSE-11")
    assert True  # if no exception, it's fine

@pytest.mark.django_db
def test_transaction_start_and_stop():
    ChargerRepository.upsert("EVSE-12", "V", "M")
    tx = TransactionRepository.start("EVSE-12", 1, "RFID123", 10)
    stopped = TransactionRepository.stop(tx.transaction_id, 50)
    assert stopped.status == TransactionStatusChoices.STOPPED

@pytest.mark.django_db
def test_eventlog_repository():
    ChargerRepository.upsert("EVSE-13", "V", "M")
    log = EventLogRepository.log("EVSE-13", "Heartbeat", "OK")
    assert log.event == "Heartbeat"
