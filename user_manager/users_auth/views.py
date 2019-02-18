from django.http.response import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from rest_auth.models import TokenModel


@csrf_exempt
def verify_token(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        username = request.POST.get('username')

        if token and username:
            tokens = TokenModel.objects.filter(key=token, user__username=username)
            if tokens.exists():
                return JsonResponse({'is_valid': True, 'user_id': tokens.first().user_id}, status=200)
    return JsonResponse({'is_valid': False, 'user_id': None}, status=400)

