from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import EthereumAuthSerializer, UserSerializer
from django.contrib.auth import get_user_model
import secrets
import string

User = get_user_model()

class NonceView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, address):
        # Generate a random nonce
        alphabet = string.ascii_letters + string.digits
        nonce = ''.join(secrets.choice(alphabet) for i in range(32))
        
        # Get or create user and update nonce
        user, created = User.objects.get_or_create(
            wallet_address__iexact=address,
            defaults={
                'wallet_address': address.lower(),
                'username': address.lower(),
                'nonce': nonce
            }
        )
        
        if not created:
            user.nonce = nonce
            user.save()
        
        return Response({'nonce': nonce})

class EthereumLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = EthereumAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        validated_data = serializer.validate(serializer.validated_data)
        user = validated_data['user']
        token = validated_data['token']
        
        user_serializer = UserSerializer(user)
        
        return Response({
            'user': user_serializer.data,
            'token': token
        })

class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)