# Generated by Django 4.2.4 on 2023-08-24 17:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='first_name',
            field=models.CharField(help_text=('Обязательное к заполнению поле. ', 'Максимальная длина - 30 символов.'), max_length=30, verbose_name='Полное имя'),
        ),
    ]
