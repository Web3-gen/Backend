from rest_framework import serializers
from .models import WaitlistEntry


class WaitlistEntrySerializer(serializers.ModelSerializer):
    email = serializers.EmailField()

    class Meta:
        model = WaitlistEntry
        fields = ["email"]

    def create(self, validated_data):
        return WaitlistEntry.objects.create(**validated_data)

    # def to_representation(self, instance):
    #     if isinstance(instance, dict):  # Handle the case where validated_data is passed
    #         return instance
    #     # Customize the response format for model instances
    #     return {
    #         "email": instance.email,
    #         "registered_at": instance.created_at.isoformat() if instance.created_at else None,
    #     }
