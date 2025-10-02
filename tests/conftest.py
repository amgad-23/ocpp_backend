import pytest
from rest_framework.test import APIClient

from django.contrib.auth.models import User


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin", password="admin", email="admin@test.com"
    )


@pytest.fixture
def api_client():
    return APIClient()
