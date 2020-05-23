from django.urls import path
from items.views import (
    TransferRequestListView,
    accept_transfer_request,
    cancel_transfer_request,
    dispatch,
    take_in,
)


app_name = 't_orders'
urlpatterns = [
    path('', TransferRequestListView.as_view(), name='list'),
    path('accept_transfer_request/', accept_transfer_request, name='accept_transfer_request'),
    path('cancel_transfer_request/', cancel_transfer_request, name='cancel_transfer_request'),
    path('dispatch/', dispatch, name='dispatch'),
    path('take_in/', take_in, name='take_in'),

]
