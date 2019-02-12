from django.db.models import F
from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from rest_framework import generics

from quiz.models import Game, VoteLog
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
    queryset = VoteLog.objects.all()[:2]
    serializer_class = VotePollSerializer
    # TODO: Check whether we should use some permission classes

    def perform_create(self, serializer):
        votelog = serializer.save()
        Game.objects.filter(id=votelog.game, player=votelog.player).update(
            result=F('result') + votelog.points)
