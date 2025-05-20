from rest_framework import serializers

from .models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for the Notification model.
    """
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['user', 'id' ,'is_read', 'created_at']