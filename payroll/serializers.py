from rest_framework import serializers
from .models import PayRoll
from user_profile.serializers import (
    RecipientProfileSerializer,
    OrganizationProfileSerializer,
)


class PayRollSerializer(serializers.ModelSerializer):
    """
    Serializer for the PayRoll model.
    """

    recipient_details = RecipientProfileSerializer(source="recipient", read_only=True)
    organization_details = OrganizationProfileSerializer(
        source="organization", read_only=True
    )

    class Meta:
        model = PayRoll
        fields = [
            "id",
            "recipient",
            "recipient_details",
            "organization",
            "organization_details",
            "amount",
            "batch_reference",
            "description",
            "date",
            "created_at",
            "paid_at",
            "status",
            "is_paid",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "paid_at",
            "is_paid",
            "recipient_details",
            "organization_details",
        ]

    def validate(self, data):
        """
        Custom validation - Removed duplicate payroll restriction
        Organizations can now create multiple payrolls for the same recipient on the same date
        """
        # You can add other validation rules here if needed
        # For example, validate amount is positive, date is not in future, etc.

        amount = data.get("amount")
        if amount and amount <= 0:
            raise serializers.ValidationError("Amount must be greater than 0")

        return data
