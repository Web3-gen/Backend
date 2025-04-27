from rest_framework import serializers
from .models import OrganizationProfile, RecipientProfile




class RecipientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for RecipientProfile model.
    """

    class Meta:
        model = RecipientProfile
        fields = ['id', 'name', 'email', 'organization', 'recipient_ethereum_address', 
                    'recipient_phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def to_representation(self, instance):
        """
        Customize the representation of the RecipientProfile instance.
        """
        return {
            "id": instance.id,
            "name": instance.name,
            "organization": instance.organization.name,
            "wallet_address": instance.user.wallet_address,
            "created_at": instance.created_at.isoformat() if instance.created_at else None,
            "updated_at": instance.updated_at.isoformat() if instance.updated_at else None,
        }
    
class OrganizationProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for OrganizationProfile model.
    """
    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    recipients = RecipientProfileSerializer(many=True, read_only=True)
    

    class Meta:
        model = OrganizationProfile
        fields = ['id', 'name', 'email', 'organization_address', 'organization_phone', 'recipients', 'created_at', 'updated_at']
    
