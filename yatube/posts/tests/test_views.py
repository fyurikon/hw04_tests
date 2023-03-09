from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class TaskPagesTests(TestCase):
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

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            id=11,
            group=cls.group
        )

        for _ in range(30):
            cls.post = Post.objects.create(
                text='Один из многих',
                author=cls.user,
                group=cls.group,
            )

        cls.special_group = Group.objects.create(
            title='Особая группа',
            slug='special-slug',
            description='Особое описание',
        )

        cls.special_post = Post.objects.create(
            text='Это особенный пост!',
            author=cls.user,
            id=666,
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
                kwargs={'post_id': 11}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': 11}
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
        total_posts_on_page = len(response.context['page_obj'])

        self.assertEqual(total_posts_on_page, 10)
        self.assertIn('page_obj', response.context)

    def test_group_list_page_show_correct_context(self):
        """Index page with correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': 'some-slug'}
            )
        )

        first_object = response.context['page_obj'][0]
        total_posts_on_page = len(response.context['page_obj'])

        self.assertEqual(total_posts_on_page, 10)
        self.assertIn('page_obj', response.context)
        self.assertEqual(
            first_object.group.title,
            self.group.title
        )
        self.assertEqual(
            first_object.group.description,
            self.group.description
        )
        self.assertEqual(
            first_object.group.slug,
            self.group.slug
        )

    def test_profile_page_show_correct_context(self):
        """Profile page with correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': 'HasNoName'}
            )
        )

        first_object = response.context['page_obj'][0]
        total_posts_on_page = len(response.context['page_obj'])

        self.assertEqual(total_posts_on_page, 10)
        self.assertIn('page_obj', response.context)
        self.assertEqual(
            first_object.author.username,
            self.user.username
        )

    def test_post_detail_page_show_correct_context(self):
        """Post detail page with correct context."""
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )

        first_object = response.context['post']

        self.assertEqual(
            first_object.text,
            self.post.text
        )
        self.assertEqual(
            first_object.author.username,
            self.user.username
        )
        self.assertEqual(
            first_object.group,
            self.post.group
        )

    def test_post_create_page_show_correct_context(self):
        """Post create page with post_create method with correct context."""
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

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

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_special_post_on_three_pages(self):
        """Special post is available on index, profile, group_list."""
        page_names = {
            reverse('posts:index'): self.special_group.slug,
            reverse(
                'posts:profile',
                kwargs={
                    'username': self.user.username
                }
            ): self.special_group.slug,
            reverse(
                'posts:group_list',
                kwargs={
                    'slug': self.special_group.slug
                }
            ): self.special_group.slug,
        }

        for value, expected in page_names.items():
            response = self.authorized_client.get(value)
            special_object = response.context['page_obj'][0]

            with self.subTest(value=value):
                self.assertEqual(special_object.group.slug, expected)

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

        casual_object = response.context['page_obj'][0]

        self.assertNotEqual(casual_object, self.special_post)
        self.assertNotEqual(casual_object.group.slug, self.special_group.slug)
