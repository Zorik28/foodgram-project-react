from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db.models import (CASCADE, CharField, CheckConstraint, EmailField,
                              F, ForeignKey, Model, Q, UniqueConstraint)


class CustomUser(AbstractUser):
    email = EmailField(
        verbose_name='Электронная почта', max_length=254, unique=True)
    username = CharField(
        verbose_name='Логин',
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message='Введите корректный username',
            code='invalid_username'
        )])
    first_name = CharField(verbose_name='Имя', max_length=150)
    last_name = CharField(verbose_name='Фамилия', max_length=150)
    password = CharField(verbose_name='Пароль', max_length=150)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']


class Subscribe(Model):
    User = get_user_model()
    user = ForeignKey(
        User,
        related_name='followers',
        verbose_name='Подписчик',
        on_delete=CASCADE
    )
    author = ForeignKey(
        User,
        related_name='followings',
        verbose_name='Автор',
        on_delete=CASCADE
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'),
            CheckConstraint(
                check=~Q(user=F('author')), name='not_follow_yourself')
        ]
