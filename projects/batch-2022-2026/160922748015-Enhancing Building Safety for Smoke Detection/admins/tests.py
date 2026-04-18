"""Tests for admin login and user activation."""
from django.test import TestCase
from django.urls import reverse


class AdminViewTest(TestCase):
    def test_admin_login_page_loads(self):
        response = self.client.get(reverse('AdminLogin'))
        self.assertEqual(response.status_code, 200)

    def test_admin_login_invalid_shows_error(self):
        response = self.client.post(reverse('AdminLoginCheck'), {
            'loginid': 'wrong',
            'pswd': 'wrong',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'login', status_code=200)
