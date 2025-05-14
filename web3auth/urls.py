from django.urls import path
from .views import NonceView, EthereumLoginView, UserDetailView, VerifyAddressView

urlpatterns = [
    path("nonce/<str:address>/", NonceView.as_view(), name="nonce"),
    path("login/", EthereumLoginView.as_view(), name="ethereum-login"),
    path("user/", UserDetailView.as_view(), name="user-detail"),
    path(
        "verify-address/<str:address>/",
        VerifyAddressView.as_view(),
        name="verify-address-detail",
    ),
]
