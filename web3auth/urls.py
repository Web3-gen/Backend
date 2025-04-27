from django.urls import path
from .views import NonceView, EthereumLoginView, UserDetailView

urlpatterns = [
    path('nonce/<str:address>/', NonceView.as_view(), name='nonce'),
    path('login/', EthereumLoginView.as_view(), name='ethereum-login'),
    path('user/', UserDetailView.as_view(), name='user-detail'),
]