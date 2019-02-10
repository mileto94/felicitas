from django.db import models


class Game(models.Model):
    """Represent each player's games."""

    # TODO: Save in Redis info for available polls per game
    player = models.PositiveIntegerField()
    result = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'

    def __str__(self):
        return f'ID: {self.id} by player {self.player}'
