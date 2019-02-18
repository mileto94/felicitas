from django.urls import path

from users_auth.views import verify_token

urlpatterns = [
    path('verify-token/', verify_token, name='verify-token'),
]
