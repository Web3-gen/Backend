from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationProfileView, RecipientProfileView

router = DefaultRouter()
router.register(
    r"organization-profile", OrganizationProfileView, basename="organization-profile"
)
router.register(
    r"recipient-profile", RecipientProfileView, basename="recipient-profile"
)

urlpatterns = [
    path("", include(router.urls)),
]
