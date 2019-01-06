from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect

from admin_auth.forms import RegistrationForm


def admin_register(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin:index')

    elif request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # Make user staff and make it Game creator]
            my_group = Group.objects.get(name='Game creator')
            my_group.user_set.add(user)
            user.is_staff = True
            user.save()

            # authenticate user
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)

            return redirect('admin:index')

    else:
        form = RegistrationForm()

    return render(request, 'admin_auth/registration.html', {'form': form})
