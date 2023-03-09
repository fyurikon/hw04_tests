from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()
PUB_DATE_DESC: str = '-pub_date'


class Group(models.Model):
    """
    Group model is responsible for the group.
    """
    title = models.CharField('Заголовок', max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Post model is responsible for the post.
    """
    text = models.TextField(
        'Текст',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )

    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts_group',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )

    class Meta:
        ordering = (PUB_DATE_DESC,)
        verbose_name = 'Публикация'
        verbose_name_plural = 'Публикации'

    def __str__(self):
        return self.text[:15]


class CensoredWord(models.Model):
    """
    Prohibited words.
    """
    word = models.CharField('Запретное слово', max_length=50)

    class Meta:
        verbose_name = 'Слово'
        verbose_name_plural = 'Слова'

    def __str__(self):
        return self.word
