"""
Tests for the users app: login, registration, prediction input validation, dataset view.
"""
import os
import tempfile
from django.test import TestCase
from django.urls import reverse
from .models import UserRegistrationModel
from django.contrib.auth.hashers import make_password


class UserRegistrationTest(TestCase):
    """Test user registration and login."""

    def test_register_page_loads(self):
        response = self.client.get(reverse('UserRegister'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'form', count=None)

    def test_login_page_loads(self):
        response = self.client.get(reverse('UserLogin'))
        self.assertEqual(response.status_code, 200)

    def test_login_invalid_credentials_returns_error(self):
        response = self.client.post(reverse('UserLoginCheck'), {
            'loginid': 'nonexistent',
            'pswd': 'wrongpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid', status_code=200)

    def test_login_activated_user_succeeds(self):
        UserRegistrationModel.objects.create(
            name='Test User',
            loginid='testuser',
            password=make_password('TestPass123'),
            mobile='9876543210',
            email='test@example.com',
            locality='Loc',
            address='Address',
            city='City',
            state='State',
            status='activated',
        )
        response = self.client.post(reverse('UserLoginCheck'), {
            'loginid': 'testuser',
            'pswd': 'TestPass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'VIEW DATASET', status_code=200)

    def test_login_not_activated_shows_message(self):
        UserRegistrationModel.objects.create(
            name='Test User',
            loginid='waituser',
            password=make_password('TestPass123'),
            mobile='9876543211',
            email='wait@example.com',
            locality='Loc',
            address='Address',
            city='City',
            state='State',
            status='waiting',
        )
        response = self.client.post(reverse('UserLoginCheck'), {
            'loginid': 'waituser',
            'pswd': 'TestPass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'not activated', status_code=200)


class PredictionViewTest(TestCase):
    """Test prediction view: page load and input validation."""

    def test_prediction_page_loads(self):
        response = self.client.get(reverse('prediction'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SENSOR', status_code=200)

    def test_prediction_missing_input_returns_error(self):
        response = self.client.post(reverse('prediction'), {
            'Temperature[C]': '20',
            'Humidity[%]': '50',
            # missing other fields
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Missing input', status_code=200)

    def test_prediction_invalid_number_returns_error(self):
        response = self.client.post(reverse('prediction'), {
            'Temperature[C]': 'not-a-number',
            'Humidity[%]': '50',
            'TVOC[ppb]': '0',
            'eCO2[ppm]': '400',
            'Raw H2': '12000',
            'Raw Ethanol': '18000',
            'Pressure[hPa]': '940',
            'PM1.0': '0',
            'PM2.5': '0',
            'NC0.5': '0',
            'NC1.0': '0',
            'NC2.5': '0',
            'CNT': '0',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid number', status_code=200)


class DatasetViewTest(TestCase):
    """Test dataset view."""

    def test_dataset_page_returns_200(self):
        response = self.client.get(reverse('DatasetView'))
        self.assertEqual(response.status_code, 200)
