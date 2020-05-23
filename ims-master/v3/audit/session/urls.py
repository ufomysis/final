from django.urls import path
from audit.views import (
    AuditSessionListView,
    AuditSessionDetailView,
    audit_score_update,
    session_delete_view,
    session_create_view,
    session_note_update,
    get_report,
    session_mark_done,


)

app_name = 'audit_session'
urlpatterns = [
    path('', AuditSessionListView.as_view(), name='list'),
    path('create/', session_create_view, name='create'),
    path('<str:pk>/', AuditSessionDetailView.as_view(), name='detail'),
    path('<str:pk>/session_mark_done/', session_mark_done, name='session_mark_done'),
    path('<str:session_id>/audit_score_update/', audit_score_update, name='score_update'),
    path('<str:pk>/session_delete_view/', session_delete_view, name='delete'),
    path('<str:session_id>/session_note_update/', session_note_update, name='session_note_update'),
    path('<str:session_id>/get_report/', get_report, name='get_report'),


]
