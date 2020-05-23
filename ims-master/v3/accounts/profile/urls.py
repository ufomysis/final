from django.urls import path
from accounts.views import user_profile_update, user_profile_update, user_profile_detail_view


app_name = 'profile'
urlpatterns = [
    path('', user_profile_detail_view, name='home'),
    path('edit/', user_profile_update, name='user_profile_update'),


]