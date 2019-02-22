from django import forms
from django.forms.formsets import formset_factory

from game_rules.models import Poll, Answer


class UploadPollsForm(forms.Form):
    polls_file = forms.FileField()


class AddPollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = '__all__'
