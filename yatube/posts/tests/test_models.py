from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create(username='HasNoName')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='some-slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_models_have_correct_object_names(self):
        """Check that __str__ method is correct."""
        group = PostModelTest.group
        post = PostModelTest.post

        self.assertEqual(group.title, group.__str__())
        self.assertEqual(post.text[:15], post.__str__())

    def test_models_have_correct_help_text(self):
        """Check that models have correct help text."""
        post = PostModelTest.post

        help_text_text = post._meta.get_field('text').help_text
        help_text_group = post._meta.get_field('group').help_text

        self.assertEqual(help_text_text, 'Введите текст поста')
        self.assertEqual(
            help_text_group, 'Группа, к которой будет относиться пост'
        )

    def test_models_have_correct_verbose_names(self):
        """Check that models have correct verbose names."""
        post = PostModelTest.post

        verbose_text_text = post._meta.get_field('text').verbose_name
        verbose_text_group = post._meta.get_field('group').verbose_name
        verbose_text_author = post._meta.get_field('author').verbose_name
        verbose_pub_date = post._meta.get_field('pub_date').verbose_name

        self.assertEqual(verbose_text_text, 'Текст')
        self.assertEqual(verbose_text_group, 'Группа')
        self.assertEqual(verbose_text_author, 'Автор')
        self.assertEqual(verbose_pub_date, 'Дата публикации')
