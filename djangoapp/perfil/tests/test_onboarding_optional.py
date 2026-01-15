import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from djangoapp.perfil.models import Perfil


@pytest.mark.django_db
def test_optional_onboarding_partial_progress():
    """
    User can fill optional onboarding in multiple steps.
    Progress increases but does not complete early.
    """
    # Arrange
    user = User.objects.create_user(
        username="jorge",
        password="123456",
        first_name="",
        last_name="",
    )
    Perfil.objects.create(
        usuario=user,
        onboarding_required_completed=True,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    # Act — first partial update
    response = client.patch(
        "/api/onboarding/optional/",
        {"first_name": "Jorge"},
        format="json",
    )

    # Assert
    assert response.status_code == 200
    assert response.data["optional_progress"] == 25
    assert response.data["onboarding_optional_completed"] is False

    # Act — second partial update
    response = client.patch(
        "/api/onboarding/optional/",
        {"last_name": "Cabral"},
        format="json",
    )

    assert response.status_code == 200
    assert response.data["optional_progress"] == 50
    assert response.data["onboarding_optional_completed"] is False