from .views import LeaveRequestView
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"leave_requests", LeaveRequestView, basename="leave_requests")
urlpatterns = [
    path("", include(router.urls)),
]