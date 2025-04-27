from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import User
from eth_account.messages import defunct_hash_message
from eth_account import Account
import jwt
from django.conf import settings
import secrets
import string

User = get_user_model()

class EthereumAuthSerializer(serializers.Serializer):
    address = serializers.CharField()
    signature = serializers.CharField()

    def validate(self, data):
        address = data.get('address')
        signature = data.get('signature')

        # Get or create user
        try:
            user = User.objects.get(wallet_address__iexact=address)
        except User.DoesNotExist:
            # Create new web3 user
            user = User.objects.create_user(
                wallet_address=address.lower(),
                username=address.lower()
            )
        
        # Verify the signature
        message = f"I'm signing my one-time nonce: {user.nonce}"
        
        try:
            # Hash the message
            message_hash = defunct_hash_message(text=message)
            # Recover the address from the signature
            recovered_address = Account.recover_message(
                message_hash,
                signature=signature
            ).lower()
        except:
            raise serializers.ValidationError("Invalid signature or message.")
        
        # Check if the recovered address matches the provided address
        if recovered_address != address.lower():
            raise serializers.ValidationError("Address and signature don't match.")
        
        # Generate a new nonce for next login
        alphabet = string.ascii_letters + string.digits
        user.nonce = ''.join(secrets.choice(alphabet) for i in range(32))
        user.save()
        
        # Generate JWT token
        payload = {
            'user_id': user.id,
            'address': user.wallet_address,
            'username': user.get_username()
        }
        token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
        
        return {
            'user': user,
            'token': token
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'wallet_address')