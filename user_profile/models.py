from django.db import models
from django.conf import settings


class OrganizationProfile(models.Model):
    """
    Organization profile model to store organization information.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    organization_address = models.TextField(blank=True, null=True)
    organization_phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Organization Profiles"


class RecipientProfile(models.Model):
    """
    Recipient profile model to store recipient information.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE, related_name='recipients')
    recipient_ethereum_address = models.CharField(max_length=42, unique=True)
    recipient_phone = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Recipient Profiles"