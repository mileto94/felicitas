"""felicitas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from game_rules.views import (
    get_next_poll, get_polls_per_game_type, get_poll_help, get_game_description,
    get_active_games, collect_game_polls, get_games_data)


urlpatterns = [
    path('next-poll/<int:game_id>/<int:poll_id>/', get_next_poll, name='next-poll'),
    path('all-polls/<int:game_id>/', get_polls_per_game_type, name='all-polls'),
    path('poll-help/<int:poll_id>/', get_poll_help, name='poll-help'),
    path('game-info/<int:game_id>/', get_game_description, name='game-info'),
    path('games-list/', get_active_games, name='games-list'),
    path('cache-polls/', collect_game_polls, name='cache-polls'),
    path('games-data/', get_games_data, name='games-data'),
]
