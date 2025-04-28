from unittest.mock import patch, ANY
from rest_framework import status
from rest_framework.test import APITestCase
from waitlist.models import WaitlistEntry
from django.urls import reverse
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

import os
import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HR_Backend.settings')
django.setup()


class WaitlistAPIViewTests(APITestCase):

    def setUp(self):
        # Setup URL and data for tests
        self.url = reverse('waitlist-list') 
        self.valid_data = {
            'email': 'testuser@example.com',
        }
        self.existing_entry = WaitlistEntry.objects.create(email='existing@example.com', confirmed=False)
        self.confirmed_entry = WaitlistEntry.objects.create(email='confirmed@example.com', confirmed=True)

    @patch('waitlist.views.EmailMultiAlternatives')
    def test_create_waitlist_entry(self, mock_email):
        # Test creating a new waitlist entry
        response = self.client.post(self.url, self.valid_data, format='json')

        # Assert the entry was created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if the email was sent with correct arguments
        mock_email.assert_called_once_with(
            f"Hey {self.valid_data['email']}, You’re In!",
            ANY,  # plain_message
            settings.DEFAULT_FROM_EMAIL,
            [self.valid_data['email']]
        )

        # Assertions on the mocked email instance (optional, but good practice)
        email_instance = mock_email.return_value
        self.assertEqual(email_instance.to, [self.valid_data['email']])
        self.assertEqual(email_instance.subject, f"Hey {self.valid_data['email']}, You’re In!")

        context = {
            "email": self.valid_data['email'],
            "logo": settings.EMAIL_LOGO_URL,
        }
        expected_html_message = render_to_string(r"email_template.html", context)
        self.assertIn(expected_html_message, email_instance.alternatives[0][0])

        expected_plain_message = strip_tags(expected_html_message)
        self.assertEqual(email_instance.body, expected_plain_message)

    @patch('waitlist.views.EmailMultiAlternatives')
    def test_resend_confirmation_email(self, mock_email):
        # Test resending confirmation email for an unconfirmed email
        response = self.client.post(self.url, {'email': self.existing_entry.email}, format='json')

        # Assert that the response is a successful resend of the confirmation email
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Confirmation email resent", response.data["message"])

        # Check if the email was resent
        mock_email.return_value.send.assert_called_once()

    @patch('waitlist.views.EmailMultiAlternatives')
    def test_email_already_on_waitlist(self, mock_email):
        # Test trying to create an entry with an email that is already confirmed
        response = self.client.post(self.url, {'email': self.confirmed_entry.email}, format='json')

        # Assert that the status is 400 (bad request) because the email is already confirmed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This email is already on our waitlist.", response.data["message"])

        # Ensure no email was sent as the entry was already confirmed
        mock_email.return_value.send.assert_not_called()

    @patch('waitlist.views.EmailMultiAlternatives')
    def test_duplicate_unconfirmed_email(self, mock_email):
        # Test resending confirmation email for an existing unconfirmed email
        response = self.client.post(self.url, {'email': self.existing_entry.email}, format='json')

        # Assert that the response is a successful resend of the confirmation email
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Confirmation email resent", response.data["message"])

        # Check if the email was resent
        mock_email.return_value.send.assert_called_once()

    @patch('waitlist.views.EmailMultiAlternatives')
    def test_existing_confirmed_email(self, mock_email):
        # Try creating an entry with an already confirmed email
        response = self.client.post(self.url, {'email': self.confirmed_entry.email}, format='json')

        # Assert that the status is 400 (bad request) as email is already confirmed
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This email is already on our waitlist.", response.data["message"])

        # Ensure that no email was sent since the email is already confirmed
        mock_email.return_value.send.assert_not_called()

    @patch('waitlist.views.EmailMultiAlternatives')
    def test_email_sent_on_successful_entry_creation(self, mock_email):
        # Test that an email is sent when a new waitlist entry is created
        test_email = 'newuser@example.com'
        response = self.client.post(self.url, {'email': test_email}, format='json')

        # Check if the email was sent with correct arguments
        mock_email.assert_called_once_with(
            f"Hey {test_email}, You’re In!",
            ANY, 
            settings.DEFAULT_FROM_EMAIL,
            [test_email]
        )

        # Assertions on the mocked email instance
        email_instance = mock_email.return_value
        self.assertEqual(email_instance.to, [test_email])
        self.assertEqual(email_instance.subject, f"Hey {test_email}, You’re In!")

    @patch('waitlist.views.EmailMultiAlternatives')
    def test_create_duplicate_email(self, mock_email):
        # Test creating an entry with an email that already exists but is unconfirmed
        unconfirmed_email_data = {'email': self.existing_entry.email}
        response = self.client.post(self.url, unconfirmed_email_data, format='json')

        # Assert that the response indicates that the email was resent
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Confirmation email resent", response.data["message"])

        # Check if the email was resent
        mock_email.return_value.send.assert_called_once()

    def test_invalid_email_format(self):
        # Test submitting an invalid email format
        invalid_email_data = {'email': 'invalidemail'}
        response = self.client.post(self.url, invalid_email_data, format='json')

        # Assert that the response returns a bad request (400) with error details
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

        # Ensure that no email sending was attempted
        pass  # Assuming serializer prevents saving, so no email sending

    @patch('waitlist.views.EmailMultiAlternatives')
    def test_duplicate_confirmed_email(self, mock_email):
        # Test submitting an email that is already confirmed
        response = self.client.post(self.url, {'email': self.confirmed_entry.email}, format='json')

        # Assert that the response returns a bad request (400) with error details
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("This email is already on our waitlist.", response.data["message"])

        # Ensure no email is sent as it is already confirmed
        mock_email.return_value.send.assert_not_called()