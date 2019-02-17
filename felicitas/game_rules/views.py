from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404

from game_rules.models import Poll, GameType


def get_next_poll(request, game_id, poll_id):
    """Get serialized data for poll per game type."""
    polls = Poll.objects.filter(
        id=poll_id, game_id=game_id, game__is_active=True
    ).prefetch_related('answers')

    if polls.exists():
        poll = polls.first()
    else:
        return Http404('This poll does not exist!')

    data = model_to_dict(poll)
    answers = [model_to_dict(ans) for ans in poll.answers.all()]
    data['answers'] = answers

    return JsonResponse(data)


def get_polls_per_game_type(request, game_id):
    """Get list of ids of available polls per game_id."""
    ids = list(Poll.objects.filter(
        game_id=game_id, game__is_active=True).values_list('id', flat=True))
    return JsonResponse({'polls': ids})


def get_poll_help(request, poll_id):
    """Get help of selected poll."""
    poll = get_object_or_404(Poll, id=poll_id)
    return JsonResponse({'help_text': poll.help_text})


def get_game_description(request, game_id):
    """Get info of selected game type."""
    game_type = get_object_or_404(GameType, id=game_id)
    return JsonResponse({'game_info': game_type.description, 'game_id': game_id})


def get_active_games(request):
    """Get info of selected game type."""
    games = GameType.objects.filter(is_active=True).only(
        'name', 'description', 'polls_count', 'image')
    data = [
        {
            'name': game.name,
            'description': game.description,
            'polls_count': game.polls_count,
            'image': game.image.url if game.image else 'img/portfolio/02-thumbnail.jpg'
        }
        for game in games
    ]
    return JsonResponse({'games': data})
