from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import OrganizationProfile, RecipientProfile
from .serializers import OrganizationProfileSerializer, RecipientProfileSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from notifications.models import Notification
from web3auth.models import User
import secrets
import string


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
            is_read=False,
        )
        notification.save()

    @action(detail=False, methods=["get"])
    def get_organization_recipients(self, request):
        """
        Retrieve all recipients associated with the authenticated organization.
        """
        try:
            organization = OrganizationProfile.objects.get(user=self.request.user.id)
            recipients = organization.recipients.all()
            serializer = RecipientProfileSerializer(recipients, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OrganizationProfile.DoesNotExist:
            return Response(
                {"detail": "Organization profile not found."},
                status=status.HTTP_404_NOT_FOUND,
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
        Filter recipients based on user type:
        - Organizations see their recipients
        - Recipients see their own profile
        """
        user = self.request.user
        try:
            organization = OrganizationProfile.objects.get(user=user)
            return RecipientProfile.objects.filter(organization=organization)
        except OrganizationProfile.DoesNotExist:
            return RecipientProfile.objects.filter(user=user)

    def create(self, request, *args, **kwargs):
        """
        Create a new recipient profile
        """
        try:
            # Get the organization profile
            organization = OrganizationProfile.objects.get(user=request.user)

            # Create new user for recipient
            ethereum_address = request.data.get("recipient_ethereum_address")

            # Check if a user with this ethereum address already exists
            user, created = User.objects.get_or_create(
                wallet_address=ethereum_address,
                defaults={
                    "username": ethereum_address,
                    "user_type": "recipient",
                    "nonce": "".join(
                        secrets.choice(string.ascii_letters + string.digits)
                        for _ in range(32))
                },
            )

            # Check if recipient profile already exists for this user
            if RecipientProfile.objects.filter(user=user).exists():
                return Response(
                    {"detail": "A recipient profile already exists for this ethereum address"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Create mutable copy of request.data
            data = request.data.copy()
            data["organization"] = organization.id
            data["user"] = user.id

            serializer = self.get_serializer(data=data)  # Use the copied data
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

            notification = Notification.objects.create(
                user=request.user,
                type="recipientAdded",
                message="New recipient has been added successfully.",
                is_read=False,
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except OrganizationProfile.DoesNotExist:
            return Response(
                {"detail": "Only organizations can create recipient profiles"},
                status=status.HTTP_403_FORBIDDEN,
            )

    def perform_create(self, serializer):
        """
        Associate the recipient with the organization during creation
        """
        serializer.save()
