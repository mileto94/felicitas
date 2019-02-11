from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from quiz.models import Game


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
