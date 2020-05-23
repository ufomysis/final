from django.urls import path

from .views import (
    InventoryListView,
    SerialListView,
    ItemListView,
    edit_quantity,
    deregister,
    send_transfer_request,
    get_barcodes,
    get_barcodes_all,


)

app_name = 'items'
urlpatterns = [

    path('', InventoryListView.as_view(), name='branch_list'),

    path('<str:branch_slug>/', SerialListView.as_view(), name='serial_list'),
    path('<str:branch_slug>/<str:iabstract_slug>/', ItemListView.as_view(), name='item_list'),
    path('<str:branch_slug>/<str:iabstract_slug>/edit_q/', edit_quantity, name='edit_quantity'),
    path('<str:branch_slug>/<str:iabstract_slug>/deregister/', deregister, name='deregister'),
    path('<str:branch_slug>/<str:iabstract_slug>/send_transfer_request/', send_transfer_request,
         name='send_transfer_request'),

    path('<str:branch_slug>/<str:iabstract_slug>/get_barcodes/', get_barcodes, name='get_barcodes'),
    path('<str:branch_slug>/<str:iabstract_slug>/get_barcodes_all/', get_barcodes_all, name='get_barcodes_all'),

]
