from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class GameType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    questions_settings = JSONField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Game Type'
        verbose_name_plural = 'Game Types'

    def __str__(self):
        return self.name
