from rest_framework import serializers

from quiz.models import Game, VoteLog


class VotePollSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteLog
        fields = '__all__'


class NewGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('game_type', 'player')

    def __init__(self, *args, **kwargs):
        super(NewGameSerializer, self).__init__(*args, **kwargs)
        self.fields['game_type'].required = True
        self.fields['player'].required = True


class EndGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('id', )

    def __init__(self, *args, **kwargs):
        super(EndGameSerializer, self).__init__(*args, **kwargs)
        self.fields['id'].required = True
        self.fields['id'].read_only = False


class GameScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ('game_type', 'player', 'result')
