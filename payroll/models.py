from django.db import models
from user_profile.models import RecipientProfile

class PayRoll(models.Model):
    """
    Model to store payroll information for users.
    """
    user = models.ForeignKey(RecipientProfile, on_delete=models.CASCADE, related_name='payrolls')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Payroll for {self.user.username} - {self.date}"