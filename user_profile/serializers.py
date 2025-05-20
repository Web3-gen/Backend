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
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = RecipientProfile
        fields = [
            "id",
            "name",
            "email",
            "user",
            "organization",
            "recipient_ethereum_address",
            "recipient_phone",
            "salary",
            "position",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
        extra_kwargs = {
            "recipient_ethereum_address": {"required": True},
            "email": {"required": True},
            "name": {"required": True},
        }

    def validate(self, attrs):
        # Validate required fields first
        if not attrs.get("recipient_ethereum_address"):
            raise serializers.ValidationError(
                {"recipient_ethereum_address": "This field is required."}
            )
        if not attrs.get("email"):
            raise serializers.ValidationError({"email": "This field is required."})

        # Convert ethereum address to lowercase
        attrs["recipient_ethereum_address"] = attrs[
            "recipient_ethereum_address"
        ].lower()

        # Check for existing ethereum address
        if RecipientProfile.objects.filter(
            recipient_ethereum_address__iexact=attrs["recipient_ethereum_address"]
        ).exists():
            raise serializers.ValidationError(
                {
                    "recipient_ethereum_address": "This ethereum address is already registered."
                }
            )

        return attrs

    def create(self, validated_data):
        organization = self.context.get("organization")
        if not organization:
            raise serializers.ValidationError(
                {"organization": "Organization is required"}
            )

        # Create user first
        User = get_user_model()
        user, created = User.objects.get_or_create(
            wallet_address__iexact=validated_data["recipient_ethereum_address"],
            defaults={
                "wallet_address": validated_data["recipient_ethereum_address"],
                "username": validated_data["recipient_ethereum_address"],
                "user_type": "recipient",
                "nonce": "".join(
                    secrets.choice(string.ascii_letters + string.digits)
                    for i in range(32)
                ),
            },
        )

        try:
            # Create recipient profile
            recipient_profile = RecipientProfile.objects.create(
                user=user, organization=organization, **validated_data
            )
            return recipient_profile
        except Exception as e:
            if created:
                user.delete()  # Cleanup if user was just created
            raise


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
