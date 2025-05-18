from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.decorators import action
from django.db import transaction
from .models import OrganizationProfile, RecipientProfile
from .serializers import OrganizationProfileSerializer, RecipientProfileSerializer
from notifications.models import Notification


class IsOrganization(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_organization


class IsRecipient(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_recipient


class OrganizationProfileView(ModelViewSet):
    """
    Viewset for handling organization profile operations.
    """

    queryset = OrganizationProfile.objects.all()
    serializer_class = OrganizationProfileSerializer
    permission_classes = [IsAuthenticated, IsOrganization]

    def get_queryset(self):
        """
        Optionally restricts the returned profiles to a given user,
        by filtering against a `user` query parameter in the URL.
        """
        return super().get_queryset().filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if not request.user.is_organization:
            raise serializers.ValidationError(
                "User must have organization privileges to create organization profiles"
            )

        try:
            instance = OrganizationProfile.objects.get(user=request.user)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except OrganizationProfile.DoesNotExist:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            with transaction.atomic():
                self.perform_create(serializer)
                # Update user type if they're becoming both
                if request.user.user_type == "recipient":
                    request.user.user_type = "both"
                    request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        with transaction.atomic():
            serializer.save(user=self.request.user)
            Notification.objects.create(
                user=self.request.user,
                type="organizationAdded",
                message="Your organization profile has been created successfully.",
                is_read=False,
            )

    @action(detail=False, methods=["get"])
    def get_organization_recipients(self, request):
        """
        Retrieve all recipients associated with the authenticated organization.
        """
        try:
            organization = OrganizationProfile.objects.get(user=self.request.user)
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

    @transaction.atomic
    def perform_create(self, serializer):
        try:
            if not self.request.user.is_organization:
                raise serializers.ValidationError(
                    "User must have organization privileges to create recipient profiles"
                )
            organization = OrganizationProfile.objects.get(user=self.request.user)
            serializer.context["organization"] = organization
            recipient = serializer.save()

            Notification.objects.create(
                user=self.request.user,
                type="recipientAdded",
                message=f"New recipient {recipient.name} has been added successfully.",
                is_read=False,
            )

        except OrganizationProfile.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "Organization profile not found"}
            )

    @action(detail=False, methods=["post"])
    @transaction.atomic
    def batch_create(self, request):
        if not request.user.is_organization:
            raise serializers.ValidationError(
                "Only organizations can create recipient profiles"
            )

        try:
            organization = OrganizationProfile.objects.get(user=request.user)
        except OrganizationProfile.DoesNotExist:
            raise serializers.ValidationError("Organization profile not found")

        recipients_data = request.data.get("recipients", [])
        if not recipients_data:
            raise serializers.ValidationError("No recipients data provided")

        created_recipients = []
        errors = []

        for recipient_data in recipients_data:
            serializer = self.get_serializer(data=recipient_data)
            try:
                if serializer.is_valid(raise_exception=True):
                    recipient = serializer.save(organization=organization)
                    created_recipients.append(recipient)
            except Exception as e:
                errors.append(
                    {
                        "recipient": recipient_data.get("email", "Unknown"),
                        "errors": str(e),
                    }
                )
                continue

        if created_recipients:
            Notification.objects.create(
                user=request.user,
                type="recipientsAdded",
                message=f"Successfully added {len(created_recipients)} recipients.",
                is_read=False,
            )

        return Response(
            {
                "success": len(created_recipients),
                "failed": len(errors),
                "created_recipients": RecipientProfileSerializer(
                    created_recipients, many=True
                ).data,
                "errors": errors if errors else None,
            },
            status=(
                status.HTTP_201_CREATED
                if created_recipients
                else status.HTTP_400_BAD_REQUEST
            ),
        )

    def perform_update(self, serializer):
        """
        Ensure only recipients can update their own profiles
        """
        try:
            # Get the recipient profile being updated
            instance = self.get_object()

            # Check if the user is updating their own profile
            if instance.user != self.request.user:
                raise serializers.ValidationError(
                    {"detail": "You can only update your own profile"}
                )

            # Check if user is a recipient
            if not self.request.user.is_recipient:
                raise serializers.ValidationError(
                    {"detail": "User must have recipient privileges to update recipient profiles"}
                )

            # Save and create notification
            serializer.save()
            Notification.objects.create(
                user=self.request.user,
                type="recipientUpdated",
                message="Recipient profile updated successfully.",
                is_read=False
            )

        except RecipientProfile.DoesNotExist:
            raise serializers.ValidationError(
                {"detail": "Recipient profile not found"}
            )