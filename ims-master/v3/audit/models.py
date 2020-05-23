from django.db import models
import uuid

from django.contrib.auth import get_user_model
from branches.models import Branch
from django.core.validators import RegexValidator
# from utils.utils import NAME_REGEX

USER = get_user_model()

class AuditForm(models.Model):
    added_by = models.ForeignKey(USER, null=True, on_delete=models.SET_NULL)
    title = models.CharField(max_length=60,
                             # validators=[
                             #     RegexValidator(
                             #         regex=NAME_REGEX,
                             #         message='ชื่อต้องประกอบด้วยตัวอักขระเท่านั้น'
                             #     )],
                             )
    description = models.TextField(blank=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = [
            'title', 'updated'
        ]

class AuditQuestion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=150)
    form = models.ForeignKey(AuditForm, on_delete=models.CASCADE, related_name='questions')


    def __str__(self):
        return self.question


AUDITSESSION_STATUS_CHOICES = (
    ('in_progress', 'IN_PROGRESS'),
    ('done', 'DONE'),

)


class AuditSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=60,
                             # validators=[
                             #     RegexValidator(
                             #         regex=NAME_REGEX,
                             #         message='ชื่อต้องประกอบด้วยตัวอักขระเท่านั้น'
                             #     )],
                             )
    branch = models.ForeignKey(Branch, null=True, on_delete=models.SET_NULL)
    audit_date = models.DateTimeField(auto_now=False, auto_now_add=True, blank=True)
    audit_form = models.ForeignKey(AuditForm, on_delete=models.CASCADE, related_name='session_form')
    timestamp = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=15, default='in_progress', choices=AUDITSESSION_STATUS_CHOICES)
    auditor = models.ForeignKey(USER,  null=True, on_delete=models.SET_NULL, related_name='session_auditor')
    note = models.TextField(blank=True)
    questions = models.ManyToManyField(AuditQuestion, blank=True, through='Audit_Score', related_name='audit_sessions')

    class Meta:
        ordering = [
            'title', 'timestamp'
        ]

    def __str__(self):
        return self.title

AUDIT_SCORE_CHOICES = (
    ('pass', 'ผ่าน'),
    ('fail', 'ไม่ผ่าน'),
    ('unknown', 'ยังไม่ประเมินผล'),

)
class Audit_Score(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(AuditSession, blank=True, on_delete=models.CASCADE, related_name='audit_score_session')
    question = models.ForeignKey(AuditQuestion, blank=True, on_delete=models.CASCADE, related_name='audit_score_question')
    score_pass = models.CharField(max_length=30, default='unknown', choices=AUDIT_SCORE_CHOICES)
    note = models.CharField(max_length=120, blank=True)

    def __str__(self):
        return self.session.title


