from rest_framework import serializers
from .models import PayRoll
from user_profile.serializers import RecipientProfileSerializer, OrganizationProfileSerializer

class PayRollSerializer(serializers.ModelSerializer):
    """
    Serializer for the PayRoll model.
    """
    recipient_details = RecipientProfileSerializer(source='recipient', read_only=True)
    organization_details = OrganizationProfileSerializer(source='organization', read_only=True)
    
    class Meta:
        model = PayRoll
        fields = [
            'id',
            'recipient',
            'recipient_details',
            'organization',
            'organization_details',
            'amount',
            'batch_reference',
            'description',
            'date',
            'created_at',
            'paid_at',
            'status',
            'is_paid'
        ]
        read_only_fields = ['id', 'created_at', 'paid_at', 'is_paid']

    def validate_amount(self, value):
        """
        Validate that amount is positive
        """
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero")
        return value

    def validate(self, data):
        """
        Custom validation to ensure organization can't create duplicate payrolls
        for the same recipient on the same date
        """
        recipient = data.get('recipient')
        organization = data.get('organization')
        date = data.get('date')
        
        # Check if this is an update operation
        instance = self.instance
        if instance is None:  # This is a create operation
            if PayRoll.objects.filter(
                recipient=recipient,
                organization=organization,
                date=date
            ).exists():
                raise serializers.ValidationError(
                    "A payroll entry already exists for this recipient on this date"
                )
        
        return data
