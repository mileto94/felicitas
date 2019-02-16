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


class GameInfoUpdateSerializer(serializers.Serializer):
    game_id = serializers.IntegerField()
    game_info = serializers.CharField()

    class Meta:
        fields = ('game_id', 'game_info')
