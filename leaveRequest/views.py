from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import action
from user_profile.views import IsOrganization, IsRecipient
from user_profile.models import RecipientProfile, OrganizationProfile
from notifications.models import Notification


class LeaveRequestView(viewsets.ModelViewSet):
    """
    Viewset for handling leave request operations.
    """

    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter leave requests based on user type and profile.
        """
        try:
            if self.request.user.is_recipient:
                recipient_profile = RecipientProfile.objects.get(user=self.request.user)
                return super().get_queryset().filter(recipient=recipient_profile)
            elif self.request.user.is_organization:
                org_profile = OrganizationProfile.objects.get(user=self.request.user)
                return super().get_queryset().filter(recipient__organization=org_profile)
            return LeaveRequest.objects.none()
        except (RecipientProfile.DoesNotExist, OrganizationProfile.DoesNotExist):
            return LeaveRequest.objects.none()

    def perform_create(self, serializer):
        """
        Create leave request with recipient profile.
        """
        try:
            if not self.request.user.is_recipient:
                raise serializers.ValidationError({
                    "detail": "User must have recipient privileges to create leave requests"
                })

            recipient_profile = RecipientProfile.objects.get(user=self.request.user)
            leave_request = serializer.save(recipient=recipient_profile)
            
            # Create notification for organization
            if recipient_profile.organization:
                Notification.objects.create(
                    user=recipient_profile.organization.user,
                    type="leaveRequestCreated",
                    message=f"New leave request from {recipient_profile.name}",
                    is_read=False
                )
            
            return leave_request
            
        except RecipientProfile.DoesNotExist:
            raise serializers.ValidationError({
                "detail": "No recipient profile found for this user"
            })

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_leave_requests(self, request):
        """
        Get leave requests based on user type and profile.
        """
        try:
            if request.user.is_recipient:
                recipient_profile = RecipientProfile.objects.get(user=request.user)
                queryset = LeaveRequest.objects.filter(recipient=recipient_profile)
            elif request.user.is_organization:
                org_profile = OrganizationProfile.objects.get(user=request.user)
                queryset = LeaveRequest.objects.filter(recipient__organization=org_profile)
            else:
                queryset = LeaveRequest.objects.none()
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except (RecipientProfile.DoesNotExist, OrganizationProfile.DoesNotExist):
            return Response({
                "error": "User profile not found"
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"], permission_classes=[IsOrganization])
    def approve_leave_request(self, request, pk=None):
        """
        Approve a leave request.
        """
        try:
            # Get organization profile
            org_profile = OrganizationProfile.objects.get(user=request.user)
            
            # Get and validate leave request
            leave_request = self.get_object()
            
            # Verify organization owns this leave request
            if leave_request.recipient.organization != org_profile:
                raise serializers.ValidationError({
                    "detail": "You don't have permission to approve this leave request"
                })
            
            leave_request.status = "approved"
            leave_request.save()
            
            # Create notification for recipient
            Notification.objects.create(
                user=leave_request.recipient.user,
                type="leaveRequestApproved",
                message="Your leave request has been approved",
                is_read=False
            )
            
            return Response({
                "status": "Leave request approved"
            }, status=status.HTTP_200_OK)
            
        except OrganizationProfile.DoesNotExist:
            return Response({
                "error": "Organization profile not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        except LeaveRequest.DoesNotExist:
            return Response({
                "error": "Leave request not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def patch_update_leave_request(self, request, pk=None):
        """
        Update a leave request.
        """
        try:
            if not request.user.is_recipient:
                raise serializers.ValidationError({
                    "detail": "User must have recipient privileges to update leave requests"
                })
                
            recipient_profile = RecipientProfile.objects.get(user=request.user)
            leave_request = self.get_object()
            
            # Verify ownership
            if leave_request.recipient != recipient_profile:
                raise serializers.ValidationError({
                    "detail": "You can only update your own leave requests"
                })
            
            serializer = self.get_serializer(
                leave_request,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except RecipientProfile.DoesNotExist:
            return Response({
                "error": "Recipient profile not found"
            }, status=status.HTTP_400_BAD_REQUEST)
        except LeaveRequest.DoesNotExist:
            return Response({
                "error": "Leave request not found"
            }, status=status.HTTP_404_NOT_FOUND)