from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

    def test_signup_url_exists_at_desired_location(self):
        """Page /users/signup/ is available."""
        response = self.guest_client.get('/auth/signup/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_signup_url_uses_correct_template(self):
        """Page /auth/signup/ template is available."""
        response = self.guest_client.get('/auth/signup/')
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_signup_page_show_correct_context(self):
        """Signup page with correct context."""
        response = self.guest_client.get(reverse('users:signup'))

        form_fields = {
            'first_name': forms.fields.CharField,
            'last_name': forms.fields.CharField,
            'username': forms.fields.CharField,
            'email': forms.fields.EmailField,
            'password1': forms.fields.CharField,
            'password2': forms.fields.CharField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_user_signup(self):
        """New user is created and added to database."""
        user_content = {
            'username': 'Rick',
            'password1': '8Rick18!#',
            'password2': '8Rick18!#'
        }

        user_nbr_before_creation = User.objects.count()

        self.guest_client.post(
            reverse('users:signup'),
            data=user_content,
        )

        user_nbr_after_creation = User.objects.count()

        self.assertNotEqual(
            user_nbr_before_creation,
            user_nbr_after_creation
        )
