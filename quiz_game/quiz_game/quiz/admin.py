from django.contrib import admin

from quiz.models import Game


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    pass
