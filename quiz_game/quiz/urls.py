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

from quiz.views import start_game, end_game, VotePerPoll


urlpatterns = [
    path('start-game/<int:game_type>/<int:user_id>/', start_game, name='start-game'),
    path('end-game/<int:game_id>/', end_game, name='end-game'),
    path('poll-vote/', VotePerPoll.as_view(), name='poll-vote'),
]
