import json

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models

from quiz_game.aws_connections import get_client


class Game(models.Model):
    """Represent each player's games."""

    player = models.PositiveIntegerField()
    game_type = models.PositiveIntegerField(default=0)
    result = models.IntegerField(default=0)
    finished = models.BooleanField(default=False)
    polls_list = ArrayField(models.PositiveIntegerField(), blank=True, null=True)
    answered_polls = ArrayField(models.PositiveIntegerField(), blank=True, null=True)

    class Meta:
        verbose_name = 'Game'
        verbose_name_plural = 'Games'

    def __str__(self):
        return f'ID: {self.id} by player {self.player}'

    def _collect_game_polls(self):
        try:
            sns_client = get_client('sns')
            response = sns_client.publish(
                TopicArn=settings.SNS_SETTINGS['collectGamePolls']['TopicArn'],
                Message=json.dumps({
                    'polls': self.polls_list,
                }),
                Subject='collectGamePolls',
                MessageStructure='collectGamePollsStructure',
                MessageAttributes={
                    'collectGamePollsStructure': {
                        'StringValue': 'collectGamePolls',
                        'DataType': 'String'
                    }
                }
            )
            print('SNS response for collectGamePolls: ', response)
        except Exception as e:
            print('Failed to send information about collectGamePolls.')
            print(e)


class VoteLog(models.Model):
    player = models.PositiveIntegerField()
    game_type = models.PositiveIntegerField()
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    vote = models.CharField(max_length=150)
    points = models.SmallIntegerField(default=0)
    poll = models.PositiveIntegerField()

    def __str__(self):
        return f'player ID {self.player} for {self.game}'
