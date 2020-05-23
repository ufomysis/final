from django.urls import path, include

from .views import (
    CurrentStockBranchReport,

)

app_name = 'reports'
urlpatterns = [

    path('', CurrentStockBranchReport, name='home'),


]
