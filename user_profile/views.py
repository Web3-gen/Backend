from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import OrganizationProfile, RecipientProfile
from .serializers import OrganizationProfileSerializer, RecipientProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action



class OrganizationProfileView(ModelViewSet):
    """
    Viewset for handling organization profile operations.
    """
    queryset = OrganizationProfile.objects.all()
    serializer_class = OrganizationProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned profiles to a given user,
        by filtering against a `user` query parameter in the URL.
        """
        return super().get_queryset().filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RecipientProfileView(ModelViewSet):
    """
    Viewset for handling recipient profile operations.
    """
    queryset = RecipientProfile.objects.all()
    serializer_class = RecipientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned profiles to a given user,
        by filtering against a `user` query parameter in the URL.
        """
        return super().get_queryset().filter(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def batch_create(self, request, *args, **kwargs):
        """
        Create multiple recipient profiles in a single request.
        """
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
