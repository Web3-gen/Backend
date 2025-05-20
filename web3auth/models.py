from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    wallet_address = models.CharField(max_length=42, unique=True, null=True, blank=True)
    nonce = models.CharField(max_length=100, null=True, blank=True)
    user_type = models.CharField(
        max_length=12,
        choices=[
            ("recipient", "Recipient"),
            ("organization", "Organization"),
            ("both", "Both"),  # Add this option
        ],
        default="organization",
    )

    def __str__(self):
        return self.wallet_address

    def get_username(self):
        return self.wallet_address

    @property
    def is_organization(self):
        return self.user_type in ["organization", "both"]

    @property
    def is_recipient(self):
        return self.user_type in ["recipient", "both"]
