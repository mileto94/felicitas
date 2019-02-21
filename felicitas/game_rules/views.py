import json

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

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

    return JsonResponse(poll.serialize_poll())


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
    return JsonResponse({
        'id': game_type.id,
        'name': game_type.name,
        'description': game_type.description,
        'polls_count': game_type.polls_count,
        'image': game_type.image.url if game_type.image else 'img/portfolio/02-thumbnail.jpg'
    })


def get_active_games(request):
    """Get info of selected game type."""
    games = GameType.objects.filter(is_active=True).only(
        'name', 'description', 'polls_count', 'image')
    data = [
        {
            'id': game.id,
            'name': game.name,
            'description': game.description,
            'polls_count': game.polls_count,
            'image': game.image.url if game.image else 'img/portfolio/02-thumbnail.jpg'
        }
        for game in games
    ]
    return JsonResponse({'games': data})


@csrf_exempt
def collect_game_polls(request):
    print('Retrieved collect game polls: ', request.data)
    message_data = json.loads(request.data.get('Message', "{}"))
    polls = Poll.objects.filter(id__in=message_data.get('polls'))

    for poll in polls:
        cache_key = settings.POLL_DATA_KEY.format(id=poll.id)
        cache.set(cache_key, poll.serialize_poll())
        print(cache_key)
        print(cache.get(cache_key))
    return JsonResponse({'status': 'OK'}, status=200)
