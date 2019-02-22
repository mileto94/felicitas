import requests
from random import shuffle

from django.conf import settings
from django.core.cache import cache


def get_available_polls(game_type_id):
    """Get data for available polls per game type id via API."""

    poll_response = requests.get(
        url=f'http://localhost:8000/all-polls/{game_type_id}/',
        timeout=0.1  # in sec
    )
    if poll_response.status_code == 200:
        return poll_response.json()
    return {}


def get_poll_data(game_type_id, poll_id):
    """Get data for poll via API."""

    poll_response = requests.get(
        url=f'http://localhost:8000/next-poll/{game_type_id}/{poll_id}/',
        timeout=0.1  # in sec
    )
    if poll_response.status_code == 200:
        return poll_response.json()
    return {}


def get_poll(game_type_id, poll_id):
    """Get data for poll via cache or API."""

    # get data for the poll from cache
    poll_key = settings.POLL_DATA_KEY.format(id=poll_id)
    print('Selected poll ID: ', poll_id)
    poll_data = cache.get(poll_key)
    if not poll_data:
        poll_data = get_poll_data(game_type_id, poll_id)
    shuffle(poll_data.get('answers'))
    return poll_data


def get_players_data(players):
    """Get data for players by id via API."""

    users_response = requests.get(
        url='http://localhost:8002/user-data/',
        params={'player_id': players},
        timeout=0.1  # in sec
    )
    if users_response.status_code == 200:
        return users_response.json().get('players')
    return {}


def get_games_data(games):
    """Get data for game name by id via API."""

    games_response = requests.get(
        url='http://localhost:8000/games-data/',
        params={'game_id': games},
        timeout=0.1  # in sec
    )
    if games_response.status_code == 200:
        return games_response.json().get('games')
    return {}
