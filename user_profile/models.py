
from django.db import models

class User(models.Model):
    """
    User model to store user profile information.
    """
    name = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=50, choices=[('organization', 'Organization'), ('recipient', 'Recipient')], default='organization')
    date_joined = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Users"

class OrganizationProfile(models.Model):
    """
    Organization profile model to store organization information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    organization_address = models.TextField(blank=True, null=True)
    organization_phone = models.CharField(max_length=15, blank=True, null=True)

    
    def __str__(self):
        return self.organization_name
    
    class Meta:
        verbose_name_plural = "Organization Profiles"


class RecipientProfile(models.Model):
    """
    Recipient profile model to store recipient information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recipient_phone = models.CharField(max_length=15, blank=True, null=True)

    
    def __str__(self):
        return self.recipient_name
    
    class Meta:
        verbose_name_plural = "Recipient Profiles"