from django.db import models
from django.core.validators import MinValueValidator
from user_profile.models import RecipientProfile, OrganizationProfile 

class PayRoll(models.Model):
    """
    Model to store payroll information for users.
    """
    recipient = models.ForeignKey(RecipientProfile, on_delete=models.CASCADE, related_name='recipients')
    organization = models.ForeignKey(OrganizationProfile, on_delete=models.CASCADE, related_name='organization')
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    batch_reference = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=30,
        choices=[
            ('pending', 'Pending'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    is_paid = models.BooleanField(default=False)

    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['batch_reference']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Payroll for {self.recipient.recipient_ethereum_address} - {self.date}"