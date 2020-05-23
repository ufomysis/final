from django.urls import path
from .views import (
    ItemAbstractListView,
    ItemAbstractCreateView,
    ItemAbstractUpdateView,
    item_abstracts_delete_view,
    item_abstract_detail_view,
    add_item,

)

app_name = 'itemabstracts'
urlpatterns = [
    path('', ItemAbstractListView.as_view(), name='list'),
    path('create/', ItemAbstractCreateView.as_view(), name='create'),
    path('<str:slug>/', item_abstract_detail_view, name='detail'),
    path('<str:slug>/additem/', add_item, name='additem'),

    path('<str:slug>/edit/', ItemAbstractUpdateView.as_view(), name='update'),
    path('<str:slug>/delete/', item_abstracts_delete_view, name='delete'),

]
