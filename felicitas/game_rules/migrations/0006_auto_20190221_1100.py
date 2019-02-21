# Generated by Django 2.1.5 on 2019-02-21 11:00

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game_rules', '0005_gametype_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gametype',
            name='polls_count',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='poll',
            name='negative_marks',
            field=models.SmallIntegerField(default=0, help_text='Enter negative number'),
        ),
        migrations.AlterField(
            model_name='poll',
            name='positive_marks',
            field=models.PositiveSmallIntegerField(default=1, help_text='Enter positive number'),
        ),
    ]
