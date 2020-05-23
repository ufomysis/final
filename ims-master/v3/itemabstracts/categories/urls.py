from django.urls import path
from itemabstracts.views import (
    CategoryListView,
    category_create_view,
    category_delete_view,

)

app_name = 'categories'
urlpatterns = [
    path('', CategoryListView.as_view(), name='list'),
    path('create/', category_create_view, name='create'),
    path('<int:pk>/delete/', category_delete_view, name='delete'),

]
