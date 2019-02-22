from unittest.mock import MagicMock, patch

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from game_rules.models import Category, GameType, Poll


class BaseFelicitasTestCase():
    def create_game(self, count=1, is_active=True):
        with patch('boto3.client', return_value=MagicMock()) as mock_sns_client:
            game_type = GameType.objects.create(
                name='Who wants to become a millionaire?',
                description='Test Description',
                is_active=is_active,
                polls_count=count,
                image=None,
            )
        if is_active:
            self.assertTrue(mock_sns_client.called)
            self.assertEqual(1, mock_sns_client.call_count)

        return game_type

    def create_category(self):
        return Category.objects.create(title='Knowledge')

    def create_user(self):
        return User.objects.create(
            username='test',
            email='test@test.com',
            is_staff=True)

    def create_poll(self, game, category, user):
        with patch('boto3.client', return_value=MagicMock()) as mock_sns_client:
            poll = Poll.objects.create(
                title='How is the weather today?',
                category=category,
                difficulty='easy',
                poll_type='single',
                help_text='Help text',
                positive_marks=1,
                negative_marks=-1,
                created_by=user,
                game=game
            )

        self.assertTrue(mock_sns_client.called)
        self.assertEqual(1, mock_sns_client.call_count)
        return poll


class TestNextPoll(BaseFelicitasTestCase, TestCase):
    def setUp(self):
        self.category = self.create_category()
        self.user = self.create_user()
        self.game = self.create_game(count=3)
        self.poll = self.create_poll(self.game, self.category, self.user)

    def test_poll_serialization(self):
        """Test serialize_poll() method of Poll model."""
        expected = {
            'id': self.poll.id,
            'title': self.poll.title,
            'category': self.poll.category_id,
            'difficulty': self.poll.difficulty,
            'poll_type': self.poll.poll_type,
            'help_text': self.poll.help_text,
            'positive_marks': self.poll.positive_marks,
            'negative_marks': self.poll.negative_marks,
            'created_by': self.poll.created_by_id,
            'game': self.poll.game_id,
            'answers': []
        }
        self.assertDictEqual(expected, self.poll.serialize_poll())

    def test_next_poll_with_existing_poll(self):
        """Test poll data schema."""
        url = reverse('next-poll', kwargs={'game_id': self.game.id, 'poll_id': self.poll.id})
        response = self.client.get(url)
        self.assertDictEqual(self.poll.serialize_poll(), response.json())

    def test_next_poll_with_not_existing_poll(self):
        url = reverse('next-poll', kwargs={'game_id': self.game.id, 'poll_id': 100})
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_next_poll_with_not_existing_game(self):
        url = reverse('next-poll', kwargs={'game_id': 100, 'poll_id': self.poll.id})
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)

    def test_next_poll_with_not_game_and_poll(self):
        url = reverse('next-poll', kwargs={'game_id': 100, 'poll_id': 100})
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)


class TestPollsPerGame(BaseFelicitasTestCase, TestCase):
    def setUp(self):
        self.category = self.create_category()
        self.user = self.create_user()
        self.game = self.create_game(count=3)
        self.poll = self.create_poll(self.game, self.category, self.user)

    def test_polls_per_existing_game(self):
        url = reverse('all-polls', kwargs={'game_id': self.game.id})
        response = self.client.get(url)
        expected = {'polls': [self.poll.id], 'count': self.game.polls_count}
        self.assertDictEqual(expected, response.json())

    def test_polls_per_non_existing_game(self):
        url = reverse('all-polls', kwargs={'game_id': 100})
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)


class TestPollHelp(BaseFelicitasTestCase, TestCase):
    def setUp(self):
        self.category = self.create_category()
        self.user = self.create_user()
        self.game = self.create_game(count=3)
        self.poll = self.create_poll(self.game, self.category, self.user)

    def test_poll_help(self):
        url = reverse('poll-help', kwargs={'poll_id': self.poll.id})
        response = self.client.get(url)
        expected = {'help_text': self.poll.help_text}
        self.assertDictEqual(expected, response.json())

    def test_poll_help_per_non_existing_poll(self):
        url = reverse('poll-help', kwargs={'poll_id': 100})
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)


class TestGameDescription(BaseFelicitasTestCase, TestCase):
    def setUp(self):
        self.category = self.create_category()
        self.user = self.create_user()
        self.game = self.create_game(count=3)
        self.poll = self.create_poll(self.game, self.category, self.user)

    def test_game_info_per_existing_game(self):
        url = reverse('game-info', kwargs={'game_id': self.game.id})
        response = self.client.get(url)
        expected = {
            'id': self.game.id,
            'name': self.game.name,
            'description': self.game.description,
            'polls_count': self.game.polls_count,
            'image': self.game.get_image_url()
        }
        self.assertDictEqual(expected, response.json())

    def test_game_info_per_non_existing_game(self):
        url = reverse('game-info', kwargs={'game_id': 100})
        response = self.client.get(url)
        self.assertEqual(404, response.status_code)


class TestActiveGames(BaseFelicitasTestCase, TestCase):
    def test_active_games_structure(self):
        """Test poll data schema."""
        self.game = self.create_game(count=3)

        url = reverse('games-list')
        response = self.client.get(url)
        expected = {
            'id': self.game.id,
            'name': self.game.name,
            'description': self.game.description,
            'polls_count': self.game.polls_count,
            'image': self.game.get_image_url()
        }
        self.assertDictEqual(expected, response.json().get('games')[0])

    def test_non_active_games(self):
        """Test poll data schema."""
        self.game = self.create_game(count=3, is_active=False)

        url = reverse('games-list')
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
