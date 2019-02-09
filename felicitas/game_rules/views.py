from django.http import JsonResponse, Http404
from django.forms.models import model_to_dict

from game_rules.models import Poll


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

