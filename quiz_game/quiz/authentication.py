from django.conf import settings
from django.core.cache import cache
from django.http.response import JsonResponse

from rest_framework import response, status


def is_authenticated(request, is_api=True):
    if not (request.data.get('token') and cache.get(
            settings.USER_TOKEN_KEY.format(token=request.data.get('token')))):
        if is_api:
            return response.Response(
                {'message': 'You are not logged in'},
                status=status.HTTP_403_FORBIDDEN)
        return JsonResponse({'message': 'You are not logged in'}, status=403)
