from django.urls import path

from .views import (
    OrderListView,
    OrderDetailView,
    order_cancel,
    order_take_back,
    order_give_items,
    order_mark_done,
    edit_note,
    get_order_report,

)

app_name = 'orders'
urlpatterns = [

    path('', OrderListView.as_view(), name='list'),
    path('<str:pk>/', OrderDetailView.as_view(), name='detail'),
    path('<str:order_id>/order_cancel/', order_cancel, name='order_cancel'),
    path('<str:order_id>/order_give_items/', order_give_items, name='order_give_items'),
    path('<str:order_id>/order_take_back/', order_take_back, name='order_take_back'),
    path('<str:order_id>/order_mark_done/', order_mark_done, name='order_mark_done'),
    path('<str:order_id>/edit_note/', edit_note, name='edit_note'),
    path('<str:order_id>/get_order_report/', get_order_report, name='get_order_report'),


]
