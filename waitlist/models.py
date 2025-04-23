from django.db import models
import uuid

class WaitlistEntry(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    confirmed = models.BooleanField(default=False)
    confirmation_token = models.UUIDField(default=uuid.uuid4, editable=False)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name_plural = "Waitlist Entries"