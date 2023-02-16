from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    '''User setting model'''

    email = models.EmailField(
        help_text='Ваш электронный адрес',
        verbose_name='Электронная почта',
        max_length=254,
        unique=True
    )

    username = models.CharField(
        help_text='Ваш логин',
        verbose_name='Логин',
        max_length=150,
        unique=True
    )
    first_name = models.CharField(
        help_text='Ваше имя',
        verbose_name='Имя',
        max_length=150
    )
    last_name = models.CharField(
        help_text='Ваша фамилия',
        verbose_name='Фамилия',
        max_length=150
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = 'username', 'first_name', 'last_name'

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.first_name[:15], self.last_name[:15]
