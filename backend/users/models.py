from django.contrib.auth.models import AbstractUser
from django.db.models import (CASCADE, BooleanField, CharField,
                              CheckConstraint, DateTimeField, EmailField,
                              ForeignKey, Model, Q)
from django.db.models.functions import Length

from api.validators import MinLenValidator

CharField.register_lookup(Length)


class CustomUser(AbstractUser):
    username = CharField(
        'Юзернейм',
        max_length=30,
        unique=True,
        help_text=('Обязательное к заполнению поле. ',
                   'Может быть от 5 до 30 символов.'),
        validators=(
            MinLenValidator(
                min_len=5,
                field='username',
            ),
        ),
    )
    first_name = CharField(
        'Полное имя',
        max_length=30,
        help_text=('Обязательное к заполнению поле. ',
                   'Максимальная длина - 30 символов.'),
    )
    last_name = CharField(
        'Фамилия',
        max_length=50,
        help_text=('Обязательное к заполнению поле. ',
                   'Максимальная длина - 50 символов.'),
    )
    email = EmailField(
        'Адрес электронной почты',
        max_length=100,
        unique=True,
        help_text=('Обязательное к заполнению поле. ',
                   'Максимальная длина - 100 символов.'),
    )
    password = CharField(
        'Пароль',
        max_length=512,
        help_text=('Обязательное к заполнению поле. ',
                   'Максимальная длина - 64 символа.'),
    )
    is_active = BooleanField(
        'Активен',
        default=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username', )
        constraints = (
            CheckConstraint(
                check=Q(username__length__gte=5),
                name='\nЮзернейм слишком короткий.\n',
            ),
        )

    def __str__(self):
        return f'{self.username}: {self.email}'


class Subscriptions(Model):
    author = ForeignKey(
        verbose_name='Подписка на автора',
        related_name='following',
        to=CustomUser,
        on_delete=CASCADE,
    )
    user = ForeignKey(
        verbose_name='Подписчик автора',
        related_name='followers',
        to=CustomUser,
        on_delete=CASCADE,
    )
    added = DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        editable=False,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user.username} подписался на: {self.author.username}'
