import pytest
from rest_framework.test import APIClient

from django.urls import reverse


class FakeCP:
    async def call(self, payload):
        # Return a fake accepted response
        return type("Resp", (), {"__dict__": {"status": "Accepted"}})()


@pytest.mark.django_db
def test_remote_start_with_mock(monkeypatch, admin_user):
    client = APIClient()

    # Auth
    resp = client.post(
        reverse("token_obtain_pair"),
        {"username": "admin", "password": "admin"},
        format="json",
    )
    token = resp.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # Mock get_cp to return a fake CP
    from ocpp_server import registry

    monkeypatch.setattr(registry, "get_cp", lambda cid: FakeCP())

    resp = client.post(
        reverse("remote_start", args=["EVSE-100"]),
        {"id_tag": "RFID-100"},
        format="json",
    )
    assert resp.status_code == 200
    assert resp.json()["response"]["status"] == "Accepted"


@pytest.mark.django_db
def test_remote_stop_with_mock(monkeypatch, admin_user):
    client = APIClient()
    resp = client.post(
        reverse("token_obtain_pair"),
        {"username": "admin", "password": "admin"},
        format="json",
    )
    token = resp.json()["access"]
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    from ocpp_server import registry

    monkeypatch.setattr(registry, "get_cp", lambda cid: FakeCP())

    resp = client.post(
        reverse("remote_stop", args=["EVSE-101"]), {"transaction_id": 1}, format="json"
    )
    assert resp.status_code == 200
    assert resp.json()["response"]["status"] == "Accepted"
