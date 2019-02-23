import json

from unittest.mock import MagicMock, patch

from django.forms.models import model_to_dict
from django.test import TestCase
from django.urls import reverse

from quiz.models import Game, VoteLog


class BaseQuizGameTestCase:
    def create_game(self, player=1, game_type=1, result=0, finished=False, polls_list=[], answered_polls=[]):
        return Game.objects.create(
            player=player,
            game_type=game_type,
            result=result,
            finished=finished,
            polls_list=polls_list,
            answered_polls=answered_polls
        )

    def create_vote_log(self, game, player=1, game_type=1, vote='', points=0, poll=1):
        return VoteLog.objects.create(
            player=player,
            game_type=game_type,
            game=game,
            vote=vote,
            points=points,
            poll=poll
        )


class TestEndGame(BaseQuizGameTestCase, TestCase):
    def setUp(self):
        self.game = self.create_game()

    def test_end_game(self):
        url = reverse('end-game')
        response = self.client.post(
            url, data={'id': self.game.id}, content_type='application/json')
        self.assertEqual(201, response.status_code)
        self.game.finished = True
        self.assertDictEqual(model_to_dict(self.game), response.json())


class TestUserActions(TestCase):
    def test_validate_token(self):
        url = reverse('validate-token')
        user_id = 1
        user_response = MagicMock(status_code=200, POST={'user_id': user_id})
        user_response.json = MagicMock(return_value={'user_id': user_id})

        with patch('requests.post', return_value=user_response) as mock_post:
            with patch('django.core.cache.cache.set') as mock_cache:
                response = self.client.post(
                    url,
                    data={'token': 'token', 'username': 'username'},
                )
                self.assertEqual(200, response.status_code)
                self.assertDictEqual({'user_id': user_id}, response.json())

            self.assertTrue(mock_cache.called)
            self.assertEqual(1, mock_cache.call_count)

        self.assertTrue(mock_post.called)
        self.assertEqual(1, mock_post.call_count)

    def test_validate_token_bad_request(self):
        url = reverse('validate-token')
        user_id = 1
        user_response = MagicMock(status_code=200, POST={'user_id': user_id})
        user_response.json = MagicMock(return_value={'user_id': user_id})

        with patch('requests.post', return_value=user_response) as mock_post:
            with patch('django.core.cache.cache.set') as mock_cache:
                response = self.client.post(
                    url,
                    data={'token': 'token', 'username': ''},
                )
                self.assertEqual(400, response.status_code)
                self.assertDictEqual({'is_active': False}, response.json())

            self.assertFalse(mock_cache.called)
            self.assertEqual(0, mock_cache.call_count)

        self.assertFalse(mock_post.called)
        self.assertEqual(0, mock_post.call_count)

    def test_log_out(self):
        url = reverse('log-out')
        user_id = 1
        with patch('django.core.cache.cache.get', return_value=user_id) as mock_cache:

            with patch('django.core.cache.cache.delete') as delete_cache:
                response = self.client.post(
                    url,
                    data={'token': 'token', 'user_id': user_id},
                )
                self.assertEqual(200, response.status_code)
                self.assertDictEqual({'status': 'OK'}, response.json())
            self.assertTrue(delete_cache.called)
            self.assertEqual(1, delete_cache.call_count)

        self.assertTrue(mock_cache.called)
        self.assertEqual(1, mock_cache.call_count)

    def test_log_out_bad_request(self):
        url = reverse('log-out')
        user_id = 1
        with patch('django.core.cache.cache.get', return_value=user_id) as mock_cache:

            with patch('django.core.cache.cache.delete') as delete_cache:
                response = self.client.post(
                    url,
                    data={'token': 'token', 'user_id': ''},
                )
                self.assertEqual(400, response.status_code)
                self.assertDictEqual({'status': 'fail'}, response.json())

            self.assertFalse(delete_cache.called)
            self.assertEqual(0, delete_cache.call_count)

        self.assertFalse(mock_cache.called)
        self.assertEqual(0, mock_cache.call_count)


class TestSNSNotifications(BaseQuizGameTestCase, TestCase):
    def test_get_retrieve_polls_update(self):
        url = reverse('game-polls-update')
        response = self.client.get(url)
        expected = {"detail": "Method \"GET\" not allowed."}
        self.assertEqual(405, response.status_code)
        self.assertDictEqual(expected, response.json())

    def test_collect_game_polls_without_cached_value(self):
        url = reverse('game-polls-update')
        data = json.dumps({"Message": '{"game_id": 8, "polls": [23, 24], "count": 10}'})
        expected = {'status': 'OK'}

        with patch('django.core.cache.cache.set', return_value=None) as mock_cache:
            response = self.client.post(url, data=data, content_type='application/json')
            self.assertEqual(200, response.status_code)
            self.assertDictEqual(expected, response.json())
        self.assertTrue(mock_cache.called)
        self.assertEqual(1, mock_cache.call_count)

    def test_get_game_info_update(self):
        url = reverse('game-info-update')
        response = self.client.get(url)
        expected = {"detail": "Method \"GET\" not allowed."}
        self.assertEqual(405, response.status_code)
        self.assertDictEqual(expected, response.json())

    def test_retrieve_game_info_update(self):
        url = reverse('game-info-update')
        data = json.dumps({"Message": '{"game_id": 10, "game_info": "Test Description"}'})
        expected = {'status': 'OK'}

        with patch('django.core.cache.cache.set', return_value=None) as mock_cache:
            response = self.client.post(url, data=data, content_type='application/json')
            self.assertEqual(200, response.status_code)
            self.assertDictEqual(expected, response.json())
        self.assertTrue(mock_cache.called)
        self.assertEqual(1, mock_cache.call_count)


class TestRankedScores(BaseQuizGameTestCase, TestCase):
    def test_get_ranked_scores_for_all_games(self):
        url = reverse('ranked-scores')
        game = self.create_game(finished=True, result=55)
        game_2 = self.create_game(finished=True, result=2)
        game_name = 'Who wants to be millionaire?'
        player = 'Username'
        expected = {
            'game_type': game_name,
            'player': player,
            'result': game.result
        }

        with patch('quiz.views.get_players_data', return_value={'1': player}) as mock_players:

            with patch('quiz.views.get_games_data', return_value={'1': game_name}) as mock_data:
                response = self.client.get(url)
                self.assertEqual(200, response.status_code)
                self.assertDictEqual(expected, response.json()[0])

            self.assertTrue(mock_data.called)
            self.assertEqual(1, mock_data.call_count)

        self.assertTrue(mock_players.called)
        self.assertEqual(1, mock_players.call_count)

    def test_get_ranked_scores_for_game_type(self):
        game = self.create_game(finished=True, result=55)
        game_2 = self.create_game(finished=True, result=56, game_type=2)
        url = reverse('ranked-scores-per-game', kwargs={'game_type_id': game.game_type})

        game_name = 'Who wants to be millionaire?'
        player = 'Username'
        expected = {
            'game_type': game_name,
            'player': player,
            'result': game.result
        }

        with patch('quiz.views.get_players_data', return_value={'1': player}) as mock_players:

            with patch('quiz.views.get_games_data', return_value={'1': game_name}) as mock_data:
                response = self.client.get(url)
                self.assertEqual(200, response.status_code)
                self.assertDictEqual(expected, response.json()[0])

            self.assertTrue(mock_data.called)
            self.assertEqual(1, mock_data.call_count)

        self.assertTrue(mock_players.called)
        self.assertEqual(1, mock_players.call_count)


class TestStartGame(BaseQuizGameTestCase, TestCase):
    def test_start_game(self):
        url = reverse('start-game')
        data = {'game_type': 1, 'player': 1}
        poll_data = {
            'id': 21,
            'title': 'What is the most common surname Wales?',
            'category': 1,
            'difficulty': 'easy',
            'poll_type': 'single',
            'help_text': '',
            'positive_marks': 1,
            'negative_marks': 0,
            'created_by': 1,
            'game': 1,
            'answers': []
        }

        with patch('django.core.cache.cache.get', return_value='{"polls": [22, 20, 21], "count": 10}') as mock_cache:

            with patch('quiz.models.Game._collect_game_polls', return_value=None) as mock_sns:
                with patch('quiz.views.get_poll', return_value=poll_data) as mock_poll:
                    response = self.client.post(url, data=data, content_type='application/json')
                    self.assertEqual(201, response.status_code)
                    response_data = response.json()
                    self.assertDictEqual(poll_data, response_data.get('poll'))

                    self.assertIn('id', response_data)
                    self.assertIsInstance(response_data['id'], int)

                    self.assertIn('player', response_data)
                    self.assertIsInstance(response_data['player'], int)

                    self.assertIn('game_type', response_data)
                    self.assertIsInstance(response_data['game_type'], int)

                    self.assertIn('result', response_data)
                    self.assertIsInstance(response_data['result'], int)

                    self.assertIn('finished', response_data)
                    self.assertFalse(response_data['finished'])

                    self.assertIn('polls_list', response_data)
                    self.assertIsInstance(response_data['polls_list'], list)

                    self.assertIn('answered_polls', response_data)
                    self.assertIsInstance(response_data['answered_polls'], list)

                    self.assertIn('polls_counter', response_data)
                    self.assertEqual(1, response_data['polls_counter'])

                self.assertTrue(mock_poll.called)
                self.assertEqual(1, mock_poll.call_count)

            self.assertTrue(mock_sns.called)
            self.assertEqual(1, mock_sns.call_count)

        self.assertTrue(mock_cache.called)
        self.assertEqual(1, mock_cache.call_count)

    def test_start_game_with_more_questions(self):
        url = reverse('start-game')
        data = {'game_type': 1, 'player': 1}
        poll_data = {
            'id': 21,
            'title': 'What is the most common surname Wales?',
            'category': 1,
            'difficulty': 'easy',
            'poll_type': 'single',
            'help_text': '',
            'positive_marks': 1,
            'negative_marks': 0,
            'created_by': 1,
            'game': 1,
            'answers': []
        }

        with patch('django.core.cache.cache.get', return_value='{"polls": [], "count": 10}') as mock_cache:
            with patch('quiz.views.get_available_polls', return_value={"polls": [22, 20, 21], "count": 10}) as mock_polls:
                with patch('quiz.models.Game._collect_game_polls', return_value=None) as mock_sns:
                    with patch('quiz.views.get_poll', return_value=poll_data) as mock_poll:
                        response = self.client.post(url, data=data, content_type='application/json')
                        self.assertEqual(201, response.status_code)
                        response_data = response.json()
                        self.assertDictEqual(poll_data, response_data.get('poll'))

                        self.assertIn('id', response_data)
                        self.assertIsInstance(response_data['id'], int)

                        self.assertIn('player', response_data)
                        self.assertIsInstance(response_data['player'], int)

                        self.assertIn('game_type', response_data)
                        self.assertIsInstance(response_data['game_type'], int)

                        self.assertIn('result', response_data)
                        self.assertIsInstance(response_data['result'], int)

                        self.assertIn('finished', response_data)
                        self.assertFalse(response_data['finished'])

                        self.assertIn('polls_list', response_data)
                        self.assertIsInstance(response_data['polls_list'], list)

                        self.assertIn('answered_polls', response_data)
                        self.assertIsInstance(response_data['answered_polls'], list)

                        self.assertIn('polls_counter', response_data)
                        self.assertEqual(1, response_data['polls_counter'])

                    self.assertTrue(mock_poll.called)
                    self.assertEqual(1, mock_poll.call_count)

                self.assertTrue(mock_sns.called)
                self.assertEqual(1, mock_sns.call_count)

            self.assertTrue(mock_polls.called)
            self.assertEqual(1, mock_polls.call_count)

        self.assertTrue(mock_cache.called)
        self.assertEqual(1, mock_cache.call_count)
