"""quiz URL Configuration

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

from quiz.views import (
    StartGame, EndGame, VotePerPoll, RetrieveGameInfoUpdate, RankedScores,
    RetrieveGamePollsUpdate, validate_token, log_out
)


urlpatterns = [
    path('start-game/', StartGame.as_view(), name='start-game'),
    path('end-game/', EndGame.as_view(), name='end-game'),
    path('poll-vote/', VotePerPoll.as_view(), name='poll-vote'),
    path('game-info-update/', RetrieveGameInfoUpdate.as_view(), name='game-info-update'),
    path('ranked-scores/', RankedScores.as_view(), name='ranked-scores'),
    path('ranked-scores/<int:game_type_id>/', RankedScores.as_view(), name='ranked-scores'),
    path('game-polls-update/', RetrieveGamePollsUpdate.as_view(), name='game-polls-update'),
    path('validate-token/', validate_token, name='validate-token'),
    path('log-out/', log_out, name='log-out'),
]
