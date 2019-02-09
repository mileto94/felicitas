from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField


class GameType(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    questions_settings = JSONField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_active = models.BooleanField(default=False)
    polls_count = models.PositiveSmallIntegerField(default=1)

    class Meta:
        verbose_name = 'Game Type'
        verbose_name_plural = 'Game Types'

    def __str__(self):
        return self.name


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
    pass


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


# class VoteLog(Model):
#     """
#     Model for saving data for single vote. Example:
#     {
#         "key": 1,  # can not be auto incremented
#         "player": 1,  # can not be auto incremented
#         "question": 1
#         "answer": "some answer",
#         "is_correct": true,
#         "town": "NY",
#         "country": "US"
#     }
#     """

#     key = NumberAttribute(hash_key=True, default=0)
#     player = NumberAttribute()
#     question = NumberAttribute()
#     answer = UnicodeAttribute()
#     is_correct = BooleanAttribute()
#     town = UnicodeAttribute()
#     country = UnicodeAttribute()

#     class Meta:
#         table_name = 'dev_votelog'

#         # Specifies the write capacity
#         write_capacity_units = 10
#         # Specifies the read capacity
#         read_capacity_units = 10

#         # TODO: for local dynamo usage
#         host = "http://localhost:8002"
