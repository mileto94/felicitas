"""felicitas URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from game_rules.views import get_next_poll, get_polls_per_game_type


urlpatterns = [
    url(r'^next-poll/(?P<game_id>\d+)/(?P<poll_id>\d+)/$', get_next_poll, name='next-poll'),
    url(r'^all-polls/(?P<game_id>\d+)/$', get_polls_per_game_type, name='all-polls')
]
