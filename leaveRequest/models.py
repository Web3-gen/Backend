from django.db import models
from user_profile.models import RecipientProfile

class LeaveRequest(models.Model):
    """
    Model to store leave request information for users.
    """

    recipient = models.ForeignKey(
        RecipientProfile,
        on_delete=models.CASCADE,
        related_name="leave_requests",
    )
    start_date = models.DateField()
    end_date = models.DateField()
    leave_type = models.CharField(
        max_length=30,
        choices=[
            ("sick", "Sick Leave"),
            ("vacation", "Vacation Leave"),
            ("personal", "Personal Leave"),
            ("other", "Other"),
        ],
    )   
    reason = models.TextField()
    status = models.CharField(
        max_length=30,
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"Leave Request from {self.recipient.name} - {self.status}"