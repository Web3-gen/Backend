from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PayRollViewSet

router = DefaultRouter()
router.register(r'payrolls', PayRollViewSet, basename='payroll')

urlpatterns = [
    path('', include(router.urls)),
]