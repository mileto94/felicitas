import json

from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse
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
        return JsonResponse({}, status=404)

    poll_data = poll.serialize_poll()

    # Cache poll info for later
    cache_key = settings.POLL_DATA_KEY.format(id=poll_id)
    cache.set(cache_key, poll_data, timeout=settings.CACHE_TIMEOUT)

    return JsonResponse(poll_data)


def get_polls_per_game_type(request, game_id):
    """Get list of ids of available polls per game_id."""
    game_type = get_object_or_404(GameType, id=game_id)
    ids = list(Poll.objects.filter(
        game_id=game_id, game__is_active=True).values_list('id', flat=True))
    return JsonResponse({'polls': ids, 'count': game_type.polls_count})


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
        'image': game_type.get_image_url()
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


def get_games_data(request, *args, **kwargs):
    data = dict(GameType.objects.filter(
        id__in=request.GET.getlist('game_id')
    ).values_list('id', 'name'))
    return JsonResponse({'games': data})


@csrf_exempt
def collect_game_polls(request):
    if request.method != 'POST' or not request.body:
        return JsonResponse({'status': 'fail'}, status=400)

    print('Retrieved collect game polls: ', request.body)

    request_data = json.loads(request.body)
    message_data = json.loads(request_data.get('Message', "{}"))
    poll_ids = message_data.get('polls')

    cache_key_pattern = settings.POLL_DATA_KEY.format(id='*')
    cached_polls = cache.keys(cache_key_pattern)

    required_polls = {}
    for poll_id in poll_ids:
        key = settings.POLL_DATA_KEY.format(id=poll_id)
        if key not in cached_polls:
            required_polls = {poll_id: key}

    if required_polls:
        polls = Poll.objects.filter(id__in=required_polls.keys())
        for poll in polls:
            cache_key = required_polls[poll.id]
            cache.set(cache_key, poll.serialize_poll(), timeout=settings.CACHE_TIMEOUT)
            print(cache_key)
            print(cache.get(cache_key))
    return JsonResponse({'status': 'OK'}, status=200)
