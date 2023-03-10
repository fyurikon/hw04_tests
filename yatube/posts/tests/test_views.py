from typing import List

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()
NUMBER_OF_POSTS: int = 15
EXPECTED_POSTS_NUMBER: int = 10
EXPECTED_POSTS_NUMBER_ON_SECOND_PAGE: int = 5
ID_FOR_TEST: int = 10


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        list_of_posts: List[Post] = []

        cls.guest_client = Client()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group
        )

        for _ in range(NUMBER_OF_POSTS):
            list_of_posts.append(
                Post(
                    text='Один из многих',
                    author=cls.user,
                    group=cls.group,
                )
            )

        Post.objects.bulk_create(list_of_posts)

        cls.special_group = Group.objects.create(
            title='Особая группа',
            slug='special-slug',
            description='Особое описание',
        )

        cls.special_post = Post.objects.create(
            text='Это особенный пост!',
            author=cls.user,
            group=cls.special_group
        )

    def test_views_uses_correct_template(self):
        """URL uses correct template."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'some-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'HasNoName'}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': ID_FOR_TEST}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': ID_FOR_TEST}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Index page with correct context."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = Post.objects.select_related(
            'author').all()[:EXPECTED_POSTS_NUMBER]

        self.assertIn('page_obj', response.context)

        page_obj = response.context['page_obj']

        for (post, post_db) in zip(page_obj, posts):
            self.assertEqual(post, post_db)

    def test_group_list_page_show_correct_context(self):
        """Index page with correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'some-slug'}
            )
        )
        posts = Post.objects.select_related(
            'author', 'group').filter(group=self.group
                                      )[:EXPECTED_POSTS_NUMBER]

        self.assertIn('page_obj', response.context)
        self.assertIn('group', response.context)

        page_obj = response.context['page_obj']

        for (post, post_db) in zip(page_obj, posts):
            self.assertEqual(post, post_db)

    def test_profile_page_show_correct_context(self):
        """Profile page with correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'HasNoName'}
            )
        )
        posts = Post.objects.select_related(
            'author', 'group').filter(author=self.user
                                      )[:EXPECTED_POSTS_NUMBER]

        self.assertIn('page_obj', response.context)
        self.assertIn('author', response.context)

        page_obj = response.context['page_obj']

        for (post, post_db) in zip(page_obj, posts):
            self.assertEqual(post, post_db)

    def test_post_detail_page_show_correct_context(self):
        """Post detail page with correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        post = response.context['post']

        self.assertEqual(post, self.post)

    def test_post_create_page_show_correct_context(self):
        """Post create page with post_create method with correct context."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        self.assertIn('is_edit', response.context)
        self.assertFalse(response.context['is_edit'])

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Post create page with post_edit method with correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.special_post.id}
            )
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        form_field_text = response.context.get('form')['text'].value()
        form_field_group = response.context.get('form')['group'].value()

        self.assertEqual(form_field_text, self.special_post.text)
        self.assertEqual(form_field_group, self.special_post.group.pk)
        self.assertIn('is_edit', response.context)
        self.assertTrue(response.context['is_edit'])

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_special_post_on_three_pages(self):
        """Special post is available on index, profile, group_list."""
        pages = (
            reverse('posts:index'),
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user.username
                }
            ),
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.special_post.group.slug
                }
            ),
        )

        for page in pages:
            response = self.authorized_client.get(page)
            page_obj = response.context['page_obj']

            self.assertIn(self.special_post, page_obj)

    def test_special_post_not_on_other_group_page(self):
        """Special post not on other group page."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.group.slug
                }
            )
        )

        page_obj = response.context['page_obj']

        self.assertNotIn(self.special_post, page_obj)


class PaginatorTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        list_of_posts: List[Post] = []

        cls.guest_client = Client()

        cls.user = User.objects.create(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

        for _ in range(NUMBER_OF_POSTS):
            list_of_posts.append(
                Post(
                    text='Один из многих',
                    author=cls.user,
                    group=cls.group,
                )
            )

        Post.objects.bulk_create(list_of_posts)

    def test_paginator_on_three_pages(self):
        """Check that paginator works on every page it meant to be."""
        group_page = '/group/some-slug/'
        profile_page = '/profile/HasNoName/'
        main_page = '/'
        second_page = '?page=2'

        page_expected_posts = {
            group_page: EXPECTED_POSTS_NUMBER,
            profile_page: EXPECTED_POSTS_NUMBER,
            main_page: EXPECTED_POSTS_NUMBER,
            group_page + second_page: EXPECTED_POSTS_NUMBER_ON_SECOND_PAGE,
            profile_page + second_page: EXPECTED_POSTS_NUMBER_ON_SECOND_PAGE,
            main_page + second_page: EXPECTED_POSTS_NUMBER_ON_SECOND_PAGE
        }

        for address, expected_number_of_posts in page_expected_posts.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                total_posts_on_page = len(response.context['page_obj'])

                self.assertEqual(
                    total_posts_on_page,
                    expected_number_of_posts
                )
