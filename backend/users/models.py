from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(verbose_name='Электронная почта', unique=True)
    username = models.CharField(
        verbose_name='Логин',
        max_length=100,
        unique=True
    )
    first_name = models.CharField(verbose_name='Имя', max_length=100)
    last_name = models.CharField(verbose_name='Фамилия', max_length=100)
    password = models.CharField(verbose_name='Пароль', max_length=100)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']


class Subscribe(models.Model):
    User = get_user_model()
    user = models.ForeignKey(
        User,
        related_name='followers',
        verbose_name='Подписчик',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='followings',
        verbose_name='Автор',
        on_delete=models.CASCADE
    )
