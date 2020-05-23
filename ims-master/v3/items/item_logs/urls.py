from django.urls import path
from items.views import (
    ItemLogListView,


)

app_name = 'item_logs'
urlpatterns = [
    path('', ItemLogListView.as_view(), name='list'),



]
