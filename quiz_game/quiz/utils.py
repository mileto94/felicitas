import requests


def get_available_polls(game_type_id, data):
    url = f'http://localhost:8000/all-polls/{game_type_id}/'
    poll_response = requests.get(url, data=data, timeout=0.05)  # in sec
    if poll_response.status_code == 200:
        poll_data = poll_response.json()
        return poll_data.get('polls', [])
    return []


def get_poll_data(game_type_id, poll_id, data):
    url = f'http://localhost:8000/next-poll/{game_type_id}/{poll_id}/'
    poll_response = requests.get(url, data=data, timeout=0.05)  # in sec
    if poll_response.status_code == 200:
        return poll_response.json()
    return {}
