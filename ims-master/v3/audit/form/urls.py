from django.urls import path
from audit.views import (
    AuditFormListView,
    AuditFormCreate,
    AuditFormDetailView,
    form_delete_view,
    AuditFormUpdateView,

)

app_name = 'audit_form'
urlpatterns = [
    path('', AuditFormListView.as_view(), name='list'),
    path('create/', AuditFormCreate.as_view(), name='create'),
    path('<int:pk>/', AuditFormDetailView.as_view(), name='detail'),
    path('<int:pk>/delete/', form_delete_view, name='delete'),
    path('<int:pk>/update/', AuditFormUpdateView.as_view(), name='update'),

]
