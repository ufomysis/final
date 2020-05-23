from django.urls import path
from itemabstracts.views import (
    UnitListView,
    unit_create_view,
    unit_delete_view,

)

app_name = 'units'
urlpatterns = [
    path('', UnitListView.as_view(), name='list'),
    path('create/', unit_create_view, name='create'),
    path('<int:pk>/delete/', unit_delete_view, name='delete'),

]
