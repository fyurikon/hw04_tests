from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
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

        cls.user_not_author = User.objects.create(username='NotAuthor')
        cls.authorized_client_not_author = Client()
        cls.authorized_client_not_author.force_login(cls.user_not_author)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

    def test_post_create_authorized(self):
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
        post = get_object_or_404(
            Post.objects.select_related
            (
                'group', 'author'
            )
        )

        self.assertEqual(post_content['text'], post.text)
        self.assertEqual(post_content['group'], post.group.pk)
        self.assertEqual(self.user.username, post.author.username)
        self.assertEqual(
            posts_nbr_before_creation + ONE_POST,
            posts_nbr_after_creation
        )

    def test_post_create_authorized_without_group(self):
        """New post is created and added to database."""
        post_content = {
            'text': 'Пост без группы'
        }

        posts_nbr_before_creation = Post.objects.count()

        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )

        posts_nbr_after_creation = Post.objects.count()
        post = get_object_or_404(
            Post.objects.select_related
            (
                'group', 'author'
            )
        )

        self.assertEqual(post_content['text'], post.text)
        self.assertEqual(post.group, None)
        self.assertEqual(self.user.username, post.author.username)
        self.assertEqual(
            posts_nbr_before_creation + ONE_POST,
            posts_nbr_after_creation
        )

    def test_post_create_not_authorized(self):
        """New post is not created by guest and not added to database."""
        post_content = {
            'text': 'Особый пост',
            'group': self.group.pk
        }

        posts_nbr_before_creation = Post.objects.count()

        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=post_content,
        )

        posts_nbr_after_creation = Post.objects.count()

        self.assertEqual(
            posts_nbr_before_creation,
            posts_nbr_after_creation
        )
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )

    def test_post_edit_authorized(self):
        """Old post is successfully edited by authorized user."""
        created_post = Post.objects.create(
            text='Особый пост',
            author=self.user,
            group=self.group
        )

        post_edited_content = {
            'text': 'Особый пост отредактирован',
            'group': self.group.pk
        }

        self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': created_post.id
                }
            ),
            data=post_edited_content
        )

        edited_post = get_object_or_404(
            Post.objects.select_related
            (
                'group', 'author'
            )
        )

        self.assertEqual(edited_post.pub_date, created_post.pub_date)
        self.assertEqual(edited_post.author, created_post.author)
        self.assertEqual(edited_post.text, post_edited_content['text'])
        self.assertEqual(edited_post.group.pk, post_edited_content['group'])

    def test_post_edit_not_authorized(self):
        """Old post is not edited by guest."""
        created_post = Post.objects.create(
            text='Особый пост',
            author=self.user,
            group=self.group
        )

        post_edited_content = {
            'text': 'Особый пост отредактирован',
            'group': self.group.pk
        }

        response = self.guest_client.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': created_post.id
                }
            ),
            data=post_edited_content
        )

        edited_post = get_object_or_404(
            Post.objects.select_related
            (
                'group', 'author'
            )
        )

        self.assertEqual(edited_post.pub_date, created_post.pub_date)
        self.assertEqual(edited_post.author, created_post.author)
        self.assertEqual(edited_post.text, created_post.text)
        self.assertEqual(edited_post.group.pk, created_post.group.pk)
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )

    def test_post_edit_authorized_not_author(self):
        """Old post is not edited by authorized user not author."""
        created_post = Post.objects.create(
            text='Особый пост',
            author=self.user,
            group=self.group
        )

        post_edited_content = {
            'text': 'Особый пост отредактирован',
            'group': self.group.pk
        }

        response = self.authorized_client_not_author.post(
            reverse(
                'posts:post_edit',
                kwargs={
                    'post_id': created_post.id
                }
            ),
            data=post_edited_content
        )

        edited_post = get_object_or_404(
            Post.objects.select_related
            (
                'group', 'author'
            )
        )

        self.assertEqual(edited_post.pub_date, created_post.pub_date)
        self.assertEqual(edited_post.author, created_post.author)
        self.assertEqual(edited_post.text, created_post.text)
        self.assertEqual(edited_post.group.pk, created_post.group.pk)
        self.assertEqual(
            response.status_code,
            HTTPStatus.FOUND
        )
