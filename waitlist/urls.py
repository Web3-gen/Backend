from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WaitlistAPIView

# Create a router and register our viewset with it.
router = DefaultRouter()
router.register(r'waitlist', WaitlistAPIView, basename='waitlist')

urlpatterns = [
    path('', include(router.urls)),
    
]
