from django.db import models
from django.conf import settings


class Notification(models.Model):
    """
    Model to store notifications for users.
    """

    choices = [
        ("recipientAdded", "Recipient Added"),
        ("recipientRemoved", "Recipient Removed"),
        ("recipientUpdated", "Recipient Updated"),
        ("organizationUpdated", "Organization Updated"),
        ("organizationAdded", "Organization Added"),
        ("organizationRemoved", "Organization Removed"),
        ("login", "Login"),
        ("payrollCreated", "Payroll Created"),
        ("payrollUpdated", "Payroll Updated"),
        ("payrollPaid", "Payroll Paid"),
        ("payrollDeleted", "Payroll Deleted"),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(max_length=100, choices=choices)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user.username} - {self.created_at}"
