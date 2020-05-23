from django import forms

from django.core.validators import MinValueValidator


class BorrowForm(forms.Form):
    amount = forms.IntegerField(label='', initial=1, required=False, validators=[MinValueValidator(1)])





