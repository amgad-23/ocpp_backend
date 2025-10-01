import pytest
from django.urls import reverse
from chargers.models import Charger, Transaction, EventLog
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_list_chargers(api_client):
    Charger.objects.create(id="EVSE-30")
    resp = api_client.get(reverse("list_chargers"))
    assert resp.status_code == 200
    assert resp.json()[0]["id"] == "EVSE-30"

@pytest.mark.django_db
def test_list_transactions(api_client):
    c = Charger.objects.create(id="EVSE-31")
    Transaction.objects.create(charger=c, connector_id=1, id_tag="X")
    resp = api_client.get(reverse("list_transactions"))
    assert resp.status_code == 200
    assert "transaction_id" in resp.json()[0]

@pytest.mark.django_db
def test_list_logs(api_client):
    c = Charger.objects.create(id="EVSE-32")
    EventLog.objects.create(charger=c, event="Boot", message="OK")
    resp = api_client.get(reverse("list_logs"))
    assert resp.status_code == 200
    assert resp.json()[0]["event"] == "Boot"

@pytest.mark.django_db
def test_list_active_chargers(api_client):
    resp = api_client.get(reverse("list_active_chargers"))
    assert resp.status_code == 200
    assert "active_chargers" in resp.json()
