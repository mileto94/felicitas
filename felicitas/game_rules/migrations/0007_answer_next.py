# Generated by Django 2.1.5 on 2019-02-22 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('game_rules', '0006_auto_20190221_1100'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='next',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='next_poll', to='game_rules.Poll'),
        ),
    ]
