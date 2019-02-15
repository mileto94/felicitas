import json

from django.core.cache import cache
from django.db.models import F
from django.http import JsonResponse, Http404, HttpResponse
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from rest_framework import generics
from rest_framework.parsers import JSONParser
from rest_framework.views import APIView

from quiz.models import Game, VoteLog
from quiz.request_parsers import PlainTextParser
from quiz.serializers import VotePollSerializer


def start_game(request, game_type, user_id):
    if not user_id:
        return Http404('Invalid user id')

    if not game_type:
        return Http404('Invalid game id')

    game = Game.objects.create(player=user_id, game_type=game_type)
    request.session['game_id'] = game.id
    return JsonResponse(model_to_dict(game))


def end_game(request, game_id):
    if not game_id:
        return Http404('Invalid user id')

    game = get_object_or_404(Game, id=game_id)
    game.finished = True
    game.save()
    request.session['game_id'] = None
    return JsonResponse(model_to_dict(game))


class VotePerPoll(generics.CreateAPIView):
    queryset = VoteLog.objects.none()
    serializer_class = VotePollSerializer
    # TODO: Check whether we should use some permission classes

    def perform_create(self, serializer):
        votelog = serializer.save()
        Game.objects.filter(id=votelog.game, player=votelog.player).update(
            result=F('result') + votelog.points)


class RetrieveGameInfoUpdate(APIView):
    queryset = VoteLog.objects.none()
    authentication_classes = ()
    permission_classes = ()
    parser_classes = (PlainTextParser, JSONParser)
    # TODO: Check whether we should use some permission classes

    def post(self, request, *args, **kwargs):
        print(args)
        print(kwargs)
        print(request.data)
        GAME_INFO_KEY = 'game-{game_id}-info'
        message_data = json.loads(request.data.get('Message', "{}"))
        game_id = message_data.get('game_id')
        game_info = message_data.get('game_info')
        if game_id and game_info:
            cache.set(
                GAME_INFO_KEY.format(game_id=game_id),
                game_info
            )
        else:
            raise ValueError('Improper information for game: {game_id}, {game_info}'.format(
                game_id=game_id, game_info=game_info
            ))
        return JsonResponse({'status': 'OK'})
