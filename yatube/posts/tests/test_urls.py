from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            id=10,
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

    def test_home_url_exists_at_desired_location(self):
        """Page available for all users."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_desired_profile_url_exists_at_desired_location(self):
        """Page /profile/user/ available for all users."""
        response = self.guest_client.get('/profile/HasNoName/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_url_exists_at_desired_location(self):
        """Page posts/post_id/ available for all users."""
        response = self.guest_client.get('/posts/10/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_url_exists_at_desired_location(self):
        """Page /group/slug/ availabale for all users."""
        response = self.guest_client.get('/group/some-slug/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_url_exists_at_desired_location(self):
        """Page /create/ available for authorized users only."""
        response_authorized = self.authorized_client.get('/create/')
        response_not_authorized = self.guest_client.get('/create/')

        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)
        self.assertEqual(response_not_authorized.status_code,
                         HTTPStatus.FOUND)

    def test_post_edit_url_exists_at_desired_location(self):
        """Page /posts/post_id/edit/ available for post author only."""
        response_authorized = self.authorized_client.get('/posts/10/edit/')
        response_not_authorized = self.guest_client.get('/posts/10/edit/')

        self.assertEqual(response_authorized.status_code, HTTPStatus.OK)
        self.assertEqual(response_not_authorized.status_code,
                         HTTPStatus.FOUND)

    def test_404_url_exists_at_desired_location(self):
        """Page /404/ exists and available for all users."""
        response = self.guest_client.get('/unexisting_page/')

        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL uses correct template."""
        templates_url_names = {
            '/group/some-slug/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            '/posts/10/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/10/edit/': 'posts/create_post.html',
            '/': 'posts/index.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
