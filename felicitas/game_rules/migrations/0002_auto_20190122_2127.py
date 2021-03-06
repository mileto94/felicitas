# Generated by Django 2.1.4 on 2019-01-22 21:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('game_rules', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Enter title for the new answer.', max_length=100)),
                ('is_correct', models.BooleanField(default=False)),
                ('next_poll', models.PositiveIntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Fill in Category title', max_length=50)),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Poll',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.TextField(help_text='Enter title for the new poll')),
                ('difficulty', models.CharField(choices=[('easy', 'easy'), ('meduim', 'meduim'), ('hard', 'hard')], help_text='Select poll type from the available types', max_length=30)),
                ('poll_type', models.CharField(choices=[('multiple', 'multiple'), ('single', 'single'), ('binary', 'binary'), ('fillin', 'fillin')], help_text='Help text for clarifying the poll', max_length=30)),
                ('help_text', models.TextField(blank=True, help_text='Enter help text for the poll', null=True)),
                ('positive_marks', models.PositiveSmallIntegerField(default=1)),
                ('negative_marks', models.SmallIntegerField(default=0)),
                ('category', models.ForeignKey(blank=True, help_text='Choose Category for the poll', null=True, on_delete=django.db.models.deletion.SET_NULL, to='game_rules.Category')),
                ('created_by', models.ForeignKey(default=1, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterModelOptions(
            name='gametype',
            options={'verbose_name': 'Game Type', 'verbose_name_plural': 'Game Types'},
        ),
        migrations.AddField(
            model_name='poll',
            name='game',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='game_rules.GameType'),
        ),
        migrations.AddField(
            model_name='answer',
            name='poll',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='answers', related_query_name='answer', to='game_rules.Poll'),
        ),
    ]
