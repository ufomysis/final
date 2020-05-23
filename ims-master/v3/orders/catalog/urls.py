from django.urls import path

from .views import (
    CatalogListView,
    CatalogDetailView,
    borrow,
    borrow_multiple,
)

app_name = 'catalog'
urlpatterns = [

    path('', CatalogListView.as_view(), name='list'),
    path('borrow_multiple/', borrow_multiple, name='borrow_multiple'),
    path('<str:info_id>/', CatalogDetailView.as_view(), name='detail'),
    path('<str:info_id>/borrow/', borrow, name='borrow'),


]
