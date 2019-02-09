from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, UnicodeSetAttribute, NumberSetAttribute,
    BooleanAttribute
)


# TODO: Create new table in Dynamo
# Poll.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

# TODO: Delete table in Dynamo
# Poll.delete_table()


class Poll(Model):
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

    key = NumberAttribute(hash_key=True, default=0)
    title = UnicodeAttribute()
    correct_answer = UnicodeAttribute()
    category = UnicodeAttribute()
    difficulty = UnicodeAttribute()
    incorrect_answers = UnicodeSetAttribute()
    poll_type = UnicodeAttribute()

    class Meta:
        table_name = 'dev_poll'

        # Specifies the write capacity
        write_capacity_units = 10
        # Specifies the read capacity
        read_capacity_units = 10

        # TODO: for local dynamo usage
        host = "http://localhost:8002"


class Player(Model):
    """
    Model for saving data for single player data. Example:
    {
        "key": "1",  # can not be auto incremented
        "names": "Joe Johnes",
        "email": "joe.johnes@gmail.con",
        "avatar": "https://s3.....",
        "town": "NY",
        "country": "US",
        "total_result": 23
    }
    """

    key = NumberAttribute(hash_key=True, default=0)
    names = UnicodeAttribute()
    email = UnicodeAttribute()
    avatar = UnicodeAttribute()
    town = UnicodeAttribute()
    country = UnicodeAttribute()
    total_result = NumberAttribute()

    class Meta:
        table_name = 'dev_player'

        # Specifies the write capacity
        write_capacity_units = 10
        # Specifies the read capacity
        read_capacity_units = 10

        # TODO: for local dynamo usage
        host = "http://localhost:8002"


# table not created yet
class Game(Model):
    """
    Model for saving data for single game. Example:
    {
        "key": 1,  # can not be auto incremented
        "player": 1,  # can not be auto incremented
        "questions": {1, 2, 3},
        "result": 2
    }
    """

    key = NumberAttribute(hash_key=True, default=0)
    player = NumberAttribute()
    questions = NumberSetAttribute()
    result = NumberAttribute()

    class Meta:
        table_name = 'dev_game'

        # Specifies the write capacity
        write_capacity_units = 10
        # Specifies the read capacity
        read_capacity_units = 10

        # TODO: for local dynamo usage
        host = "http://localhost:8002"


# table not created yet
class VoteLog(Model):
    """
    Model for saving data for single vote. Example:
    {
        "key": 1,  # can not be auto incremented
        "player": 1,  # can not be auto incremented
        "question": 1
        "answer": "some answer",
        "is_correct": true,
        "town": "NY",
        "country": "US"
    }
    """

    key = NumberAttribute(hash_key=True, default=0)
    player = NumberAttribute()
    question = NumberAttribute()
    answer = UnicodeAttribute()
    is_correct = BooleanAttribute()
    town = UnicodeAttribute()
    country = UnicodeAttribute()

    class Meta:
        table_name = 'dev_votelog'

        # Specifies the write capacity
        write_capacity_units = 10
        # Specifies the read capacity
        read_capacity_units = 10

        # TODO: for local dynamo usage
        host = "http://localhost:8002"
