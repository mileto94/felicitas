from django.contrib import admin

from game_rules.models import GameType


@admin.register(GameType)
class GameTypeAdmin(admin.ModelAdmin):
    pass
