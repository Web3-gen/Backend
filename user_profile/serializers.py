from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from .models import OrganizationProfile, RecipientProfile
from web3auth.serializers import UserSerializer
from django.contrib.auth import get_user_model
import secrets
import string


class RecipientProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for RecipientProfile model.
    """

    user = UserSerializer(read_only=True)
    #wallet_address = serializers.CharField(max_length=42, write_only=True)

    class Meta:
        model = RecipientProfile
        fields = [
            "id",
            "name",
            "email",
            "user",
            #"wallet_address",  # Added for creating new users
            "recipient_ethereum_address",
            "recipient_phone",
            "salary",
            "position",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        recipient_ethereum_address = validated_data.pop('recipient_ethereum_address')
        
        # Try to get existing user or create new one
        User = get_user_model()
        user, created = User.objects.get_or_create(
            wallet_address__iexact=recipient_ethereum_address,
            defaults={
                "wallet_address": recipient_ethereum_address.lower(),
                "username": recipient_ethereum_address.lower(),
                "user_type": "recipient",
                "nonce": "".join(secrets.choice(string.ascii_letters + string.digits) for i in range(32))
            }
        )

        # Create recipient profile
        recipient_profile = RecipientProfile.objects.create(
            user=user,
            **validated_data
        )
        return recipient_profile

    def to_representation(self, instance):
        """
        Customize the representation of the RecipientProfile instance.
        """
        return {
            "id": instance.id,
            "name": instance.name,
            "email": instance.email,  # Added missing email field
            "organization": instance.organization.name,
            "user": UserSerializer(
                instance.user
            ).data,  # Use serializer instead of direct query
            "recipient_ethereum_address": instance.recipient_ethereum_address,  # Added missing field
            "recipient_phone": instance.recipient_phone,  # Added missing field
            #"wallet_address": instance.user.wallet_address,
            "salary": instance.salary,
            "position": instance.position,
            "status": instance.status,
            "created_at": (
                instance.created_at.isoformat() if instance.created_at else None
            ),
            "updated_at": (
                instance.updated_at.isoformat() if instance.updated_at else None
            ),
        }


class OrganizationProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for OrganizationProfile model.
    """

    id = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    recipients = RecipientProfileSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    total_recipients = serializers.SerializerMethodField()

    class Meta:
        model = OrganizationProfile
        fields = [
            "id",
            "name",
            "email",
            "user",
            "organization_address",
            "organization_phone",
            "recipients",
            "total_recipients",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    @extend_schema_field(int)
    def get_total_recipients(self, obj):
        """
        Get the total number of recipients in the organization.
        Returns:
            int: The total number of recipients
        """
        return obj.recipients.count()

    def validate_email(self, value):
        """
        Validate email format and uniqueness.
        """
        if OrganizationProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value.lower()
