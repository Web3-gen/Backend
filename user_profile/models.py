from django.db import models
from django.conf import settings


class OrganizationProfile(models.Model):
    """
    Organization profile model to store organization information.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=150)
    email = models.EmailField()
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
    Each recipient is a user and belongs to an organization.
    """

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    organization = models.ForeignKey(
        OrganizationProfile, on_delete=models.CASCADE, related_name="recipients"
    )
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    recipient_ethereum_address = models.CharField(max_length=42, unique=True)
    recipient_phone = models.CharField(max_length=15, blank=True, null=True)
    salary = models.IntegerField(blank=True, null=True)
    position = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(
        max_length=30,
        choices=[("active", "Active"), ("on_leave", "On Leave")],
        default="active",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Recipient Profiles"
        # unique_together = [
        #     "user",
        #     "organization",
        # ]  # Ensure user belongs to only one organization
