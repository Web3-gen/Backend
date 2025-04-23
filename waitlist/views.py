# waitlist/api_views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.urls import reverse
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiResponse,
    OpenApiExample,
)
from .models import WaitlistEntry
from .serializers import WaitlistEntrySerializer


class WaitlistAPIView(ModelViewSet):
    queryset = WaitlistEntry.objects.all()
    serializer_class = WaitlistEntrySerializer


    def create(self, request, *args, **kwargs):
        """
        Create a new waitlist entry.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        """
        Save the new waitlist entry and send a confirmation email.
        """
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            # Check if email already exists but not confirmed
            existing = WaitlistEntry.objects.filter(email=email).first()
            if existing and not existing.confirmed:
                # Resend confirmation email
                self.send_confirmation_email(existing)
                return Response(
                    {"message": "Confirmation email resent. Please check your inbox."},
                    status=status.HTTP_200_OK,
                )
            elif existing and existing.confirmed:
                # Already confirmed
                return Response(
                    {"message": "This email is already on our waitlist."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        entry = serializer.save()
        self.send_confirmation_email(entry)


    def send_confirmation_email(self, entry):

        subject = f"Hey {entry.email}, You’re In!"

        context = {
            "email": entry.email,
            "logo": settings.EMAIL_LOGO_URL,
        }

        html_message = render_to_string(r"email_template.html", context)

        plain_message = strip_tags(html_message)

        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [entry.email]

        email = EmailMultiAlternatives(
            subject, plain_message, from_email, recipient_list
        )

        email.attach_alternative(html_message, "text/html")

        email.send()
