from rest_framework import serializers
from .models import LeaveRequest
from user_profile.serializers import RecipientProfileSerializer


class LeaveRequestSerializer(serializers.ModelSerializer):
    """
    Serializer for LeaveRequest model.
    """

    recipient = RecipientProfileSerializer(read_only=True)

    class Meta:
        model = LeaveRequest
        fields = [
            "id",
            "recipient",
            "start_date",
            "end_date",
            "leave_type",
            "reason",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]