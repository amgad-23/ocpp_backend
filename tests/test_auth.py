import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_jwt_auth_and_protected_endpoints(admin_user):
    client = APIClient()

    # Get JWT token
    resp = client.post(reverse("token_obtain_pair"),
                       {"username": "admin", "password": "admin"},
                       format="json")
    assert resp.status_code == 200
    token = resp.json()["access"]

    # Try protected endpoint without token
    no_auth = client.post(reverse("remote_start", args=["EVSE-40"]))
    assert no_auth.status_code in [401, 403]

    # With token
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    resp = client.post(reverse("remote_start", args=["EVSE-40"]),
                       {"id_tag": "RFID999"}, format="json")
    # Since no CP is connected, should return 404
    assert resp.status_code == 404
