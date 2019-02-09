from django import forms
from django.forms.formsets import formset_factory

from game_rules.models import Poll, Answer


class UploadPollsForm(forms.Form):
    polls_file = forms.FileField()


class AddPollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = '__all__'


class AddAnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = '__all__'


AddAnswerFormSet = formset_factory(AddAnswerForm, extra=2, max_num=1)
