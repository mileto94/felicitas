from django.contrib import admin

from quiz.models import Game, VoteLog


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'game_type', 'finished', 'result')
    list_per_page = 30


@admin.register(VoteLog)
class VoteLogAdmin(admin.ModelAdmin):
    list_display = ('player', 'game', 'vote', 'points')
    list_per_page = 30
