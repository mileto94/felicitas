import json

from django.conf import settings
from django.core.cache import cache
from django.db.models import F, Count, Sum
from django.forms.models import model_to_dict

from rest_framework import generics, permissions, response, status
from rest_framework.parsers import JSONParser

from quiz.models import Game, VoteLog
from quiz.request_parsers import PlainTextParser
from quiz.serializers import (
    GameInfoUpdateSerializer, NewGameSerializer, VotePollSerializer,
    EndGameSerializer, GameScoreSerializer)


class StartGame(generics.CreateAPIView):
    queryset = Game.objects.none()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )
    serializer_class = NewGameSerializer
    # TODO: Check whether we should use some permission classes

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = serializer.validated_data.get('player')
        game_type = serializer.validated_data.get('game_type')

        game = Game.objects.create(player=player, game_type=game_type)
        request.session['game_id'] = game.id

        response_data = model_to_dict(game)
        cache_key = settings.GAME_INFO_KEY.format(game_id=game_type)
        response_data['game_description'] = cache.get(cache_key)

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers)


class EndGame(generics.CreateAPIView):
    queryset = Game.objects.none()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )
    serializer_class = EndGameSerializer
    # TODO: Check whether we should use some permission classes

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        game_id = serializer.validated_data.get('id')
        games = Game.objects.filter(id=game_id)
        updated = games.update(finished=True)
        request.session['game_id'] = None

        response_data = model_to_dict(games.first()) if updated else {}

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers)


class VotePerPoll(generics.CreateAPIView):
    queryset = VoteLog.objects.none()
    serializer_class = VotePollSerializer
    # TODO: Check whether we should use some permission classes

    def perform_create(self, serializer):
        votelog = serializer.save()
        Game.objects.filter(id=votelog.game, player=votelog.player).update(
            result=F('result') + votelog.points)


class RetrieveGameInfoUpdate(generics.CreateAPIView):
    queryset = VoteLog.objects.none()
    authentication_classes = ()
    permission_classes = ()
    parser_classes = (PlainTextParser, JSONParser)
    serializer_class = GameInfoUpdateSerializer
    # TODO: Check whether we should use some permission classes

    def post(self, request, *args, **kwargs):
        print('Retrieved game info update: ', request.data)
        message_data = json.loads(request.data.get('Message', "{}"))
        serializer = self.get_serializer(data=message_data)
        serializer.is_valid(raise_exception=True)

        game_id = serializer.validated_data.get('game_id')
        game_info = serializer.validated_data.get('game_info')
        cache_key = settings.GAME_INFO_KEY.format(game_id=game_id)
        cache.set(cache_key, game_info)
        print(cache.get(cache_key))
        return response.Response({'status': 'OK'}, status=status.HTTP_200_OK)


class RankedScores(generics.ListAPIView):
    queryset = Game.objects.filter(finished=True).values(
        'game_type', 'player').annotate(result=Sum('result')).order_by('-result')
    serializer_class = GameScoreSerializer
