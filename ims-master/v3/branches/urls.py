from django.urls import path
from .views import (
    BranchListView,
    BranchDetailView,
    BranchCreateView,
    BranchUpdateView,
    branch_delete_view,

)

from accounts.views import (
    UserListView,

    user_delete_view,
    user_bulk_create_view_admin,
    user_detail_view,
    user_update_admin_view,
)

app_name = 'branches'
urlpatterns = [
    path('', BranchListView.as_view(), name='branch_list'),
    path('create/', BranchCreateView.as_view(), name='branch_create'),

    path('<str:branch_slug>/', BranchDetailView.as_view(), name='branch_detail'),
    path('<str:branch_slug>/edit/', BranchUpdateView.as_view(), name='branch_update'),
    path('<str:branch_slug>/delete/', branch_delete_view, name='branch_delete'),

    path('<str:branch_slug>/users/', UserListView.as_view(), name='user_list'),
    path('<str:branch_slug>/users/bulk_create/', user_bulk_create_view_admin, name='user_bulk_create'),
    path('<str:branch_slug>/users/<str:username>/', user_detail_view, name='user_detail'),
    path('<str:branch_slug>/users/<str:username>/delete/', user_delete_view, name='user_delete'),
    path('<str:branch_slug>/users/<str:username>/edit', user_update_admin_view, name='user_update'),


]
