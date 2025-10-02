import pytest

from chargers.models import Charger, EventLog, Transaction


@pytest.mark.django_db
def test_charger_str():
    c = Charger.objects.create(id="EVSE-001", vendor="Test", model="X")
    assert str(c) == "EVSE-001"


@pytest.mark.django_db
def test_transaction_str():
    c = Charger.objects.create(id="EVSE-002")
    t = Transaction.objects.create(charger=c, connector_id=1, id_tag="RFID123")
    assert str(t).startswith(str(t.transaction_id))


@pytest.mark.django_db
def test_eventlog_str():
    c = Charger.objects.create(id="EVSE-003")
    e = EventLog.objects.create(charger=c, event="Boot", message="Hello")
    assert "Boot" in str(e)
