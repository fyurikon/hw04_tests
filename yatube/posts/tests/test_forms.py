from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.shortcuts import get_object_or_404
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
ONE_POST: int = 1


class PostFormCreateEditTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.guest_client = Client()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

    def test_post_create(self):
        """New post is created and added to database."""
        post_content = {
            'text': 'Особый пост',
            'group': self.group.pk
        }

        posts_nbr_before_creation = Post.objects.count()

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )

        posts_nbr_after_creation = Post.objects.count()
        post = get_object_or_404(Post.objects.select_related('group', 'author'))

        self.assertEqual(post_content['text'], post.text)
        self.assertEqual(post_content['group'], post.group.pk)
        self.assertEqual(self.user.username, post.author.username)
        self.assertEqual(
            posts_nbr_before_creation + ONE_POST,
            posts_nbr_after_creation
        )

    def test_post_edit(self):
        """Old post is successfully edited."""
        post_original_content = {
            'text': 'Особый пост для редактирования',
            'group': self.group.pk
        }

        post_edited_content = {
            'text': 'Особый пост отредактирован',
            'group': self.group.pk
        }

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_original_content,
        )

        created_post = Post.objects.all()[0]

        self.authorized_client.get(
            f'/posts/{created_post.id}/edit/'
        )

        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': created_post.id
                }
            ),
            data=post_edited_content
        )

        edited_post = Post.objects.all()[0]

        self.assertNotEqual(created_post.text, edited_post.text)
