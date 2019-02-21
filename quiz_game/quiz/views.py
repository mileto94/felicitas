import json
import random
import requests

from django.conf import settings
from django.core.cache import cache
from django.db.models import F, Sum
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
from quiz.utils import get_available_polls, get_poll_data


class StartGame(generics.CreateAPIView):
    queryset = Game.objects.none()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )
    serializer_class = NewGameSerializer
    # TODO: Check whether we should use some permission classes

    def post(self, request, *args, **kwargs):
        is_authenticated(request)

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
            poll_data = get_available_polls(game_type_id, request.POST)
            cache.set(cache_polls_key, json.dumps(poll_data), timeout=None)

            available_polls, total_count = poll_data.get('polls', []), poll_data.get('count', 1)

        # select randomly the polls for this game
        try:
            game_polls = random.sample(available_polls, total_count)
        except ValueError:
            game_polls = random.choices(available_polls)
        except Exception:
            game_polls = available_polls[:1]

        # save info for selected polls per this game
        game.polls_list = game_polls
        game.save()

        first_poll_id = game_polls[0] if game_polls else 0

        # send info about desired polls to felicitas
        game._collect_game_polls()

        # get data for the poll from cache
        first_poll_key = settings.POLL_DATA_KEY.format(id=first_poll_id)
        print('First poll ID: ', first_poll_id)
        poll_data = cache.get(first_poll_key)
        if poll_data:
            poll_data = json.loads(poll_data)
        else:
            poll_data = get_poll_data(game_type_id, first_poll_id, request.POST)
            cache.set(first_poll_key, json.dumps(poll_data), timeout=settings.CACHE_TIMEOUT)

        # prepare response
        response_data = model_to_dict(game)
        response_data['poll'] = poll_data

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers)


class EndGame(generics.CreateAPIView):
    queryset = Game.objects.none()
    authentication_classes = ()
    permission_classes = (permissions.AllowAny, )
    serializer_class = EndGameSerializer
    # TODO: Check whether we should use some permission classes

    def post(self, request, *args, **kwargs):
        is_authenticated(request)

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
    # TODO: Check whether we should use some permission classes

    # def perform_create(self, serializer):
    #     votelog = serializer.save()
    #     Game.objects.filter(id=votelog.game, player=votelog.player).update(
    #         result=F('result') + votelog.points)

    def post(self, request, *args, **kwargs):
        is_authenticated(request)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        votelog = serializer.save()
        Game.objects.filter(id=votelog.game, player=votelog.player).update(
            result=F('result') + votelog.points)

        game_id = serializer.validated_data.get('id')
        games = Game.objects.filter(id=game_id)
        updated = games.update(finished=True)
        request.session['game_id'] = None

        response_data = model_to_dict(games.first()) if updated else {}

        headers = self.get_success_headers(serializer.data)
        return response.Response(
            response_data, status=status.HTTP_201_CREATED, headers=headers)


class RetrieveGameInfoUpdate(generics.CreateAPIView):
    queryset = VoteLog.objects.none()
    authentication_classes = ()
    permission_classes = ()
    parser_classes = (PlainTextParser, JSONParser)
    serializer_class = GameInfoUpdateSerializer
    # TODO: Check whether we should use some permission classes

    def post(self, request, *args, **kwargs):
        print('Retrieved game info update: ', request.data)
        message_data = json.loads(request.data.get('Message', "{}"))
        serializer = self.get_serializer(data=message_data)
        serializer.is_valid(raise_exception=True)

        game_id = serializer.validated_data.get('game_id')
        game_info = serializer.validated_data.get('game_info')
        cache_key = settings.GAME_INFO_KEY.format(game_id=game_id)
        cache.set(cache_key, game_info, timeout=None)
        print(cache.get(cache_key))
        return response.Response({'status': 'OK'}, status=status.HTTP_200_OK)


class RankedScores(generics.ListAPIView):
    queryset = Game.objects.filter(finished=True).values(
        'game_type', 'player').annotate(result=Sum('result')).order_by('-result')
    serializer_class = GameScoreSerializer


class RetrieveGamePollsUpdate(generics.CreateAPIView):
    queryset = VoteLog.objects.none()
    authentication_classes = ()
    permission_classes = ()
    parser_classes = (PlainTextParser, JSONParser)
    serializer_class = GamePollsUpdateSerializer
    # TODO: Check whether we should use some permission classes

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
        print(cache.get(cache_key))
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
