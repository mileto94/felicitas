import json

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.forms.models import model_to_dict

from felicitas.aws_connections import get_client


class GameType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    polls_count = models.PositiveSmallIntegerField(default=1)
    image = models.FileField(blank=True, null=True)

    class Meta:
        verbose_name = 'Game Type'
        verbose_name_plural = 'Game Types'

    def __str__(self):
        return self.name

    def _update_game_info(self):
        try:
            sns_client = get_client('sns')
            response = sns_client.publish(
                TopicArn=settings.SNS_SETTINGS['updateGameInfo']['TopicArn'],
                Message=json.dumps({
                    'game_id': self.id,
                    'game_info': self.description
                }),
                Subject='updateGameInfo',
                MessageStructure='updateGameInfoStructure',
                MessageAttributes={
                    'updateGameInfoStructure': {
                        'StringValue': 'updateGameInfo',
                        'DataType': 'String'
                    }
                }
            )
            print('SNS response for game info update: ', response)
        except Exception:
            print('Failed to send information about game info update.')

    def save(self, *args, **kwargs):
        super(GameType, self).save(*args, **kwargs)
        if self.is_active:
            self._update_game_info()


class BasePoll(models.Model):
    """
    Model for saving data for single poll.
    Example:
    {
        "key": 1,  # can not be auto incremented
        "category": "General Knowledge",
        "correct_answer": "Richard Branson",
        "difficulty": "easy",
        "incorrect_answers": [
            "Alan Sugar",
            "Donald Trump",
            "Bill Gates"
        ],
        "title": "Virgin Trains, Virgin Atlantic and Virgin Racing, are all companies owned by which famous entrepreneur?",
        "poll_type": "multiple"
    }
    """
    EASY = 'easy'
    MEDIUM = 'medium'
    HARD = 'hard'

    POLL_DIFFICULTIES = (
        (EASY, EASY),
        (MEDIUM, MEDIUM),
        (HARD, HARD)
    )

    POLL_TYPES = (
        ('multiple', 'multiple'),
        ('single', 'single'),
        ('binary', 'binary'),
        ('fillin', 'fillin'),
        # ('match', 'match'),
        # ('digit', 'digit')
    )

    title = models.TextField(help_text='Enter title for the new poll')
    category = models.ForeignKey('Category', help_text='Choose Category for the poll', blank=True, null=True, on_delete=models.SET_NULL)
    difficulty = models.CharField(max_length=30, choices=POLL_DIFFICULTIES, help_text='Select poll type from the available types')
    poll_type = models.CharField(max_length=30, choices=POLL_TYPES, help_text='Help text for clarifying the poll')
    help_text = models.TextField(help_text='Enter help text for the poll', blank=True, null=True)
    positive_marks = models.PositiveSmallIntegerField(default=1, help_text='')
    negative_marks = models.SmallIntegerField(default=0, help_text='')
    created_by = models.ForeignKey(User, on_delete=models.SET_DEFAULT, default=1)
    game = models.ForeignKey('GameType', on_delete=models.SET_NULL, blank=True, null=True)
    # start_time = models.DateTimeField(
    #     help_text='Select time at which the poll becomes active')
    # end_time = models.DateTimeField(
    #     help_text='Select time after which the poll becomes inactive')
    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def _update_game_polls(self):
        try:
            sns_client = get_client('sns')
            response = sns_client.publish(
                TopicArn=settings.SNS_SETTINGS['updateGamePolls']['TopicArn'],
                Message=json.dumps({
                    'game_id': self.id,
                    'polls': list(self.game.poll_set.values_list('id', flat=True)),
                    'count': self.game.polls_count
                }),
                Subject='updateGamePolls',
                MessageStructure='updateGamePollsStructure',
                MessageAttributes={
                    'updateGamePollsStructure': {
                        'StringValue': 'updateGamePolls',
                        'DataType': 'String'
                    }
                }
            )
            print('SNS response for game info update: ', response)
        except Exception as e:
            print('Failed to send information about game info update.')
            print(e)

    def save(self, *args, **kwargs):
        is_new = not self.id
        super(BasePoll, self).save(*args, **kwargs)
        if is_new and self.game:
            self._update_game_polls()

    def delete(self, *args, **kwargs):
        poll_id = self.id
        super(BasePoll, self).delete(*args, **kwargs)
        self.id = poll_id
        self._update_game_polls()


class Poll(BasePoll):
    """
    Model for saving data for single poll. Example:
    {
        "key": 1,  # can not be auto incremented
        "category": "General Knowledge",
        "correct_answer": "Richard Branson",
        "difficulty": "easy",
        "incorrect_answers": [
            "Alan Sugar",
            "Donald Trump",
            "Bill Gates"
        ],
        "title": "Virgin Trains, Virgin Atlantic and Virgin Racing, are all companies owned by which famous entrepreneur?",
        "poll_type": "multiple"
    }
    """
    def serialize_poll(self):
        data = model_to_dict(self)
        answers = [model_to_dict(ans) for ans in self.answers.all()]
        data['answers'] = answers
        return data


class Answer(models.Model):
    title = models.CharField(max_length=100, help_text='Enter title for the new answer.')
    is_correct = models.BooleanField(default=False)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name='answers', related_query_name='answer')
    next_poll = models.PositiveIntegerField(blank=True, null=True)
    # image =

    def __str__(self):
        return self.title


# class DigitAnswer(models.Model):
#     title = models.TextField(help_text='Enter title for the new answer.')
#     poll = models.ForeignKey(Poll, on_delete=models.CASCADE)

#     def __str__(self):
#         return self.title


class Category(models.Model):
    title = models.CharField(max_length=50, help_text='Fill in Category title')

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.title
