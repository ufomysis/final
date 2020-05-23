from .models import AuditForm, AuditSession, AuditQuestion, Audit_Score
from django import forms
from django.forms.models import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML


from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from django.shortcuts import render
from django.template.loader import render_to_string

from branches.models import Branch

class Formset(LayoutObject):
    template = "snippets/crispyformset.html"

    def __init__(self, formset_name_in_context, template=None, **kwargs):
        self.formset_name_in_context = formset_name_in_context
        self.fields = []

        if template:
            self.template = template

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context[self.formset_name_in_context]

        return render_to_string(self.template, {'formset': formset})



class AuditQuestionForm(forms.ModelForm):

    class Meta:
        model = AuditQuestion
        exclude = ()
        labels = {
            'question': ''
        }
        widgets = {
            'question': forms.Textarea(attrs={'cols': 140, 'rows': 1})
        }



AuditQuestionFormSet = inlineformset_factory(
    AuditForm, AuditQuestion, form=AuditQuestionForm,
    fields=['question'], extra=1, can_delete=False
    )


class AuditCreateForm(forms.ModelForm):

    class Meta:
        model = AuditForm
        exclude = ['added_by', ]

        labels = {
            'title': 'ชื่อแบบฟอร์ม',
            'description': 'คำอธิบายแบบฟอร์ม',
        }
    def __init__(self, *args, **kwargs):
        super(AuditCreateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = True


        self.helper.layout = Layout(
            Div(
                Field('title'),
                Field('description'),
                HTML('<br>'),
                Fieldset(
                    'เพิ่มคำถาม', Formset('question')
                ),
                )
            )



class CreateSessionForm(forms.Form):
    title = forms.CharField(label='ชื่อ')
    branch = forms.ModelChoiceField(queryset=Branch.objects.all(), label='สาขาที่ตรวจสอบ')
    audit_form = forms.ModelChoiceField(queryset=AuditForm.objects.all(), label='แบบฟอร์มที่ใช้ตรวจสอบ')



class AuditScoreForm(forms.ModelForm):
    class Meta:
        model = Audit_Score
        exclude = ()
        widgets = {
            'question': forms.Select(attrs={'disabled': True}),


        }
        labels = {
            'question': 'คำถาม',
            'score_pass': 'ผลการประเมิน',
            'note': 'หมายเหตุ',
        }

    def clean_question(self):

        question = self.instance.question

        return question


class SessionNoteForm(forms.Form):
    note = forms.CharField(required=False, label='ระบุหมายเหตุ')
