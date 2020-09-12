from .models import Poll, Choice
from django import forms

class PollCreateForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['title', 'question', 'question_image']

class ChoiceCreateForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text', 'choice_image']
