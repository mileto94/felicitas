from django.urls import path

from users_auth.views import verify_token, get_players_data

urlpatterns = [
    path('verify-token/', verify_token, name='verify-token'),
    path('user-data/', get_players_data, name='user-data'),
]
