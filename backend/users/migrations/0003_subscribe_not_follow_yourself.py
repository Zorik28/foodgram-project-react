# Generated by Django 4.1.1 on 2022-09-15 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_subscribe_unique_follow'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='subscribe',
            constraint=models.CheckConstraint(check=models.Q(('user', models.F('author')), _negated=True), name='not_follow_yourself'),
        ),
    ]