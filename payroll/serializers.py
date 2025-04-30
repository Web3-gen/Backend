from rest_framework import serializers

from .models import PayRoll

class PayRollSerializer(serializers.ModelSerializer):
    """
    Serializer for the PayRoll model.
    """
    class Meta:
        model = PayRoll
        fields = '__all__'
        read_only_fields = ['user', 'id' ,'is_read', 'created_at']
        