import json
import random
import requests

from django.conf import settings
from django.core.cache import cache
from django.db.models import Max
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework import generics, permissions, response, status
from rest_framework.parsers import JSONParser

from quiz.authentication import is_authenticated
from quiz.models import Game, VoteLog
from quiz.request_parsers import PlainTextParser
from quiz.serializers import (
    GameInfoUpdateSerializer, NewGameSerializer, VotePollSerializer,
    EndGameSerializer, GameScoreSerializer, GamePollsUpdateSerializer)
from quiz.utils import (
    get_available_polls, get_poll, get_players_data, get_games_data)


class StartGame(generics.CreateAPIView):
    queryset = Game.objects.none()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )
    serializer_class = NewGameSerializer

    def post(self, request, *args, **kwargs):
        missing_auth = is_authenticated(request)
        if missing_auth:
            return missing_auth

        # validate user input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        player = serializer.validated_data.get('player')
        game_type_id = serializer.validated_data.get('game_type')

        # create new game
        game = Game.objects.create(player=player, game_type=game_type_id)
        request.session['game_id'] = game.id

        cache_polls_key = settings.GAME_POLLS_KEY.format(game_id=game_type_id)
        game_data = json.loads(cache.get(cache_polls_key, "{}"))
        available_polls = game_data.get('polls', [])
        total_count = game_data.get('count')

        if not available_polls:
            poll_data = get_available_polls(game_type_id)
            cache.set(cache_polls_key, json.dumps(poll_data), timeout=None)

            available_polls, total_count = poll_data.get('polls', []), poll_data.get('count', 1)

        # select randomly the polls for this game
        try:
            game_polls = random.sample(available_polls, total_count)
        except ValueError:
            game_polls = random.choices(available_polls)
        except Exception:
            game_polls = available_polls[:1]

        first_poll_id = game_polls[0] if game_polls else 0

        # save info for selected polls per this game
        game.polls_list = game_polls[1:]
        game.answered_polls = [first_poll_id]
        game.save()

        # send info about desired polls to felicitas
        game._collect_game_polls()

        poll_data = get_poll(game_type_id, first_poll_id)

        # prepare response
        response_data = model_to_dict(game)
        response_data['polls_counter'] = len(game.answered_polls)
        response_data['poll'] = poll_data

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers)


class EndGame(generics.CreateAPIView):
    queryset = Game.objects.none()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )
    serializer_class = EndGameSerializer

    def post(self, request, *args, **kwargs):
        missing_auth = is_authenticated(request)
        if missing_auth:
            return missing_auth

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
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        missing_auth = is_authenticated(request)
        if missing_auth:
            return missing_auth

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        votelog = serializer.save()

        poll_id = serializer.validated_data.get('poll')
        poll_data = cache.get(settings.POLL_DATA_KEY.format(id=poll_id))

        # get which answer was selected
        selected_answer = {}
        for answer in poll_data.get('answers'):
            if answer.get('title') == serializer.validated_data.get('vote'):
                selected_answer = answer
                break

        # update votelog points
        if selected_answer.get('is_correct'):
            votelog.points = poll_data.get('positive_marks')
        else:
            # Poll object should contain negative mark
            votelog.points = poll_data.get('negative_marks')
        votelog.save()

        # update game total points
        game = votelog.game
        game.result = game.result + votelog.points

        # get next poll id
        poll_id = selected_answer.get('next_poll')
        if poll_id:
            # Check if next poll is special
            if poll_id in game.answered_polls:
                # If the next poll is already past, switch it.
                poll_id = None
            elif poll_id in game.polls_list:
                # If the next poll is future, remove it from future list.
                game.polls_list.pop(poll_id)

        if not poll_id:
            if len(game.answered_polls) < game.polls_count and len(game.polls_list):
                poll_id = game.polls_list[0]
                game.polls_list = game.polls_list[1:]
            else:
                game.finished = True
                game.save()
                return response.Response(model_to_dict(votelog.game), status=status.HTTP_200_OK)

        game.answered_polls.append(poll_id)
        game.save()

        poll_data = get_poll(game.game_type, poll_id)

        # prepare response
        response_data = model_to_dict(votelog.game)
        response_data['polls_counter'] = len(game.answered_polls)
        response_data['poll'] = poll_data
        print(response_data)

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers)


class RetrieveGameInfoUpdate(generics.CreateAPIView):
    queryset = VoteLog.objects.none()
    authentication_classes = ()
    permission_classes = ()
    parser_classes = (PlainTextParser, JSONParser)
    serializer_class = GameInfoUpdateSerializer

    def post(self, request, *args, **kwargs):
        print('Retrieved game info update: ', request.data)
        message_data = json.loads(request.data.get('Message', "{}"))
        serializer = self.get_serializer(data=message_data)
        serializer.is_valid(raise_exception=True)

        game_id = serializer.validated_data.get('game_id')
        game_info = serializer.validated_data.get('game_info')
        cache_key = settings.GAME_INFO_KEY.format(game_id=game_id)
        cache.set(cache_key, game_info, timeout=None)
        return response.Response({'status': 'OK'}, status=status.HTTP_200_OK)


class RankedScores(generics.ListAPIView):
    queryset = Game.objects.none()
    serializer_class = GameScoreSerializer

    def get(self, request, *args, **kwargs):
        queue = Game.objects.filter(finished=True)
        if kwargs.get('game_type_id'):
            queue = queue.filter(game_type=kwargs.get('game_type_id'))

        data = list(queue.values('game_type', 'player').annotate(
            result=Max('result')).order_by('-result')[:30])

        user_ids = []
        game_type_ids = []
        for game in data:
            user_ids.append(game['player'])
            game_type_ids.append(game['game_type'])

        players = get_players_data(user_ids)
        game_types = get_games_data(game_type_ids)

        for game in data:
            game['player'] = players.get(str(game['player']), game['player'])
            game['game_type'] = game_types.get(str(game['game_type']), game['game_type'])
        return response.Response(data)


class RetrieveGamePollsUpdate(generics.CreateAPIView):
    queryset = VoteLog.objects.none()
    authentication_classes = ()
    permission_classes = ()
    parser_classes = (PlainTextParser, JSONParser)
    serializer_class = GamePollsUpdateSerializer

    def post(self, request, *args, **kwargs):
        print('Retrieved game polls update: ', request.data)
        message_data = json.loads(request.data.get('Message', "{}"))
        serializer = self.get_serializer(data=message_data)
        serializer.is_valid(raise_exception=True)

        game_id = serializer.validated_data.get('game_id')
        game_polls = serializer.validated_data.get('polls')
        polls_count = serializer.validated_data.get('count')
        cache_key = settings.GAME_POLLS_KEY.format(game_id=game_id)
        game_data = {
            'polls': game_polls,
            'count': polls_count
        }
        cache.set(cache_key, json.dumps(game_data), timeout=None)
        return response.Response({'status': 'OK'}, status=status.HTTP_200_OK)


@csrf_exempt
def validate_token(request):
    token = request.POST.get('token')
    username = request.POST.get('username')
    if request.method == 'POST' and token and username:
        url = 'http://localhost:8002/verify-token/'
        response = requests.post(url, data=request.POST, timeout=0.05)  # in sec
        if response.status_code == 200:
            user_id = response.json().get('user_id')
            user_key = settings.USER_TOKEN_KEY.format(token=token)
            cache.set(user_key, user_id, timeout=settings.CACHE_USER_TIMEOUT)
        return JsonResponse(response.json(), status=response.status_code)
    return JsonResponse({'is_active': False}, status=400)


@csrf_exempt
def log_out(request):
    token = request.POST.get('token')
    user_id = request.POST.get('user_id')
    if request.method == 'POST' and token and user_id:
        user_key = settings.USER_TOKEN_KEY.format(token=token)
        cached_user_id = cache.get(user_key)
        if str(user_id) == str(cached_user_id):
            cache.delete(user_key)
        return JsonResponse({'status': 'OK'}, status=200)
    return JsonResponse({'status': 'fail'}, status=400)
