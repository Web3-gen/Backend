from rest_framework import serializers
from django.contrib.auth import get_user_model
from eth_account.messages import encode_defunct
from eth_account import Account
import jwt
from django.conf import settings
import secrets
import string
import logging
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta
from rest_framework_simplejwt.settings import api_settings

logger = logging.getLogger(__name__)
User = get_user_model()

class EthereumAuthSerializer(serializers.Serializer):
    address = serializers.CharField(required=True)
    signature = serializers.CharField(required=True)

    def validate(self, data):
        address = data['address'].lower()
        signature = data['signature']
        
        # Get user with case-insensitive match
        try:
            user = User.objects.get(wallet_address__iexact=address)
        except User.DoesNotExist:
            logger.warning(f"User with address {address} not found")
            return {'user': None, 'token': None}
        
        # Prepare the exact message that was signed
        message = f"I'm signing my one-time nonce: {user.nonce}"
        logger.debug(f"Verifying message: {message}")
        
        try:
            # Use encode_defunct for text messages
            message_hash = encode_defunct(text=message)
            
            # Recover the address
            recovered_address = Account.recover_message(
                message_hash,
                signature=signature
            ).lower()
            
            logger.debug(f"Recovered address: {recovered_address}, Expected: {address}")
            
            if recovered_address != address:
                logger.error("Address mismatch in signature verification")
                raise serializers.ValidationError("Address and signature don't match.")
                
        except ValueError as e:
            logger.error(f"Signature verification failed: {str(e)}")
            raise serializers.ValidationError("Invalid signature or message.") from e
        except Exception as e:
            logger.error(f"Unexpected error during verification: {str(e)}")
            raise serializers.ValidationError("Signature verification failed.") from e
        
        # Update nonce for future logins
        user.nonce = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        user.save()
        
        # Create a token with custom lifetime
        refresh = RefreshToken.for_user(user)
        
        # Calculate the expiration times correctly
        from datetime import datetime, timezone
        
        # For refresh token (7 days)
        refresh_lifetime = timedelta(days=7)
        refresh.payload["exp"] = int((datetime.now(timezone.utc) + refresh_lifetime).timestamp())
        refresh["address"] = user.wallet_address
        
        # For access token (24 hours)
        access_token = refresh.access_token
        access_lifetime = timedelta(hours=24)
        access_token.payload["exp"] = int((datetime.now(timezone.utc) + access_lifetime).timestamp())
        
        return {
            'user': user,
            'refresh': str(refresh),
            'access': str(access_token)
        }

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'wallet_address', 'user_type')