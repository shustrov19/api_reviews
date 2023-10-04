from reviewmdb_api.settings import USERNAME_CHARACTERS

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLES = (
        (USER, 'User'),
        (MODERATOR, 'Moderator'),
        (ADMIN, 'Admin'),
    )

    email = models.EmailField('Электронная почта', unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField('Тип пользователя', max_length=20,
                            choices=ROLES, default=USER)

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'

    def __str__(self):
        return self.username[:USERNAME_CHARACTERS]

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
