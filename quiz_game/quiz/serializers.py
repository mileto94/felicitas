from rest_framework import serializers

from quiz.models import VoteLog


class VotePollSerializer(serializers.ModelSerializer):
    class Meta:
        model = VoteLog
        fields = '__all__'
