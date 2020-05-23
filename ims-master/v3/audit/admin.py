from django.contrib import admin
from .models import AuditForm, AuditQuestion, Audit_Score, AuditSession
# Register your models here.
admin.site.register(Audit_Score)
admin.site.register(AuditSession)
admin.site.register(AuditQuestion)
admin.site.register(AuditForm)
