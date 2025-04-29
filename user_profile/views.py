from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import OrganizationProfile, RecipientProfile
from .serializers import OrganizationProfileSerializer, RecipientProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from notifications.models import Notification



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

    def create(self, request, *args, **kwargs):
        # Check if user already has an organization profile
        try:
            instance = OrganizationProfile.objects.get(user=request.user)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OrganizationProfile.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        
        serializer.save(user=self.request.user)
        notification = Notification.objects.create(
            user=self.request.user,
            type="organizationAdded",
            message="Your organization profile has been created successfully.",
            is_read=False
        )
        notification.save()

    @action(detail=False, methods=['get'])
    def get_organization_recipients(self, request):
        """
        Retrieve all recipients associated with the authenticated organization.
        """
        try:
            organization = OrganizationProfile.objects.get(user=request.user)
            recipients = organization.recipients.all()
            serializer = RecipientProfileSerializer(recipients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OrganizationProfile.DoesNotExist:
            return Response(
                {"detail": "Organization profile not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )



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
    
    def create(self, request, *args, **kwargs):
        # Check if user already has an organization profile
        try:
            instance = RecipientProfile.objects.get(user=request.user)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except RecipientProfile.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
    @action(detail=True, methods=['post'])
    def batch_create(self, request, *args, **kwargs):
        """
        Create multiple recipient profiles in a single request.
        """
        serializer = self.get_serializer(data=request.data, many=True)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        notification = Notification.objects.create(
            user=self.request.user,
            type="recipientAdded",
            message="New recipients have been added successfully.",
            is_read=False
        )
        notification.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
