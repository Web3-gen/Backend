from .models import LeaveRequest
from .serializers import LeaveRequestSerializer
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import action
from user_profile.views import IsOrganization, IsRecipient



class LeaveRequestView(viewsets.ModelViewSet):
    """
    Viewset for handling leave request operations.
    """

    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned leave requests to a given user,
        by filtering against a `user` query parameter in the URL.
        """
        if self.request.user.is_recipient:
            return super().get_queryset().filter(recipient=self.request.user)
        elif self.request.user.is_organization:
            return super().get_queryset().filter(recipient__organization=self.request.user)
        elif self.request.user.usertype == "both":
            return super().get_queryset().filter(
                recipient__organization=self.request.user
            )
        return []
    
    def perform_create(self, serializer):
        """
        Ensure recipient can only create leave requests for their own account
        """
        if not self.request.user.is_recipient:
            raise serializers.ValidationError(
                "User must have recipient privileges to create leave requests"
            )
        serializer.save(recipient=self.request.user)
    

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def get_leave_requests(self, request):
        """
        Get leave requests based on user type.
        
        Query Parameters:
            usertype (str, optional): Filter by user type ('recipient' or 'organization')
        """
        usertype = request.query_params.get('usertype', None)
        queryset = None
        
        try:
            if usertype == "recipient":
                recipient_profile = getattr(request.user, 'recipientprofile', None)
                if not recipient_profile:
                    raise ValueError("No recipient profile found")
                queryset = LeaveRequest.objects.filter(recipient=recipient_profile)
                
            elif usertype == "organization":
                org_profile = getattr(request.user, 'organizationprofile', None)
                if not org_profile:
                    raise ValueError("No organization profile found")
                queryset = LeaveRequest.objects.filter(recipient__organization=org_profile)
                
            else:
                queryset = self.get_queryset()
            
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except (AttributeError, ValueError) as e:
            return Response(
                {"error": str(e) or "Invalid user type or user profile not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=["post"], permission_classes=[IsOrganization])
    def approve_leave_request(self, request, pk=None):
        """
        Approve a leave request.
        """
        try:
            leave_request = self.get_object()
            leave_request.status = "approved"
            leave_request.save()
            return Response({"status": "Leave request approved"}, status=status.HTTP_200_OK)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found"}, status=status.HTTP_404_NOT_FOUND)
        
    
    def patch_update_leave_request(self, request, pk=None):
        """
        Update a leave request.
        """
        if not request.user.is_recipient:
            raise serializers.ValidationError(
                "User must have recipient privileges to update leave requests"
            )
        try:
            leave_request = self.get_object()
            serializer = self.get_serializer(leave_request, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        except LeaveRequest.DoesNotExist:
            return Response({"error": "Leave request not found"}, status=status.HTTP_404_NOT_FOUND)