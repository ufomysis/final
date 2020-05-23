from django import forms
from django.utils import timezone
from bootstrap_datepicker_plus import DatePickerInput, DateTimePickerInput




class Get_Amount_Form(forms.Form):

    amount = forms.IntegerField()


class SelectDueDateForm(forms.Form):

    due_date = forms.DateTimeField(label='', required=False, widget=DateTimePickerInput())

    def clean_due_date(self, *args, **kwargs):
        due = self.cleaned_data.get('due_date')

        if due:
            if due >= timezone.localtime():
                return due


            else:
                raise forms.ValidationError("ku")


class EditNoteForm(forms.Form):

    note = forms.CharField(label='', required=False, widget=forms.TextInput())


