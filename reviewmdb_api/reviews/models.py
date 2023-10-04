from reviewmdb_api.settings import NAME_LENGTH, TEXT_CHARACTERS
from users.models import User

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .validators import validate_year


class Category(models.Model):
    slug = models.SlugField('Slug', max_length=50, unique=True)
    name = models.CharField('Название', max_length=NAME_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


class Genre(models.Model):
    slug = models.SlugField('Slug', max_length=50, unique=True)
    name = models.CharField('Название', max_length=NAME_LENGTH)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Title(models.Model):
    name = models.CharField('Название', max_length=NAME_LENGTH)
    description = models.TextField('Описание', blank=True, null=True)
    rating = models.IntegerField('Рейтинг', blank=True, null=True,
                                 default=None)
    year = models.IntegerField('Дата выхода',
                               validators=(validate_year,),
                               db_index=True)
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='genres',
        verbose_name='Жанр'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre,
                              on_delete=models.CASCADE,
                              verbose_name='Жанр')
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              verbose_name='Произведение')

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'


class Review(models.Model):
    text = models.TextField('Текст')
    score = models.PositiveSmallIntegerField(
        'Оценка',
        default=None,
        validators=(MaxValueValidator(10, 'Оценка может быть от 1 до 10!'),
                    MinValueValidator(1, 'Оценка может быть от 1 до 10!'))
    )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews',
                              verbose_name='Произведение'
                              )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews',
                               verbose_name='Автор')

    def __str__(self):
        return self.text[:TEXT_CHARACTERS]

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('title', 'author')
        ordering = ('-pub_date',)


class Comment(models.Model):
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Отзыв')
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    text = models.TextField('Текст',)
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор')

    def __str__(self):
        return self.text[:TEXT_CHARACTERS]

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)
