"""v3 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings

from .views import home_ri, login_view, logout_view

urlpatterns = [
    path('', home_ri, name='home'),
    path('profile/', include('accounts.profile.urls'), name='profile'),

    path('login/', login_view, name='login_view'),
    path('logout/', logout_view, name='logout_view'),
    path('branch/', include('branches.urls'), name='branches'),
    path('accounts/', include('accounts.passwords.urls')),
    path('units/', include('itemabstracts.units.urls'), name='units'),
    path('categories/', include('itemabstracts.categories.urls'), name='categories'),
    path('itemabstracts/', include('itemabstracts.urls'), name='itemabstracts'),
    path('inv/', include('items.urls'), name='items'),
    path('t_orders/', include('items.t_order.urls'), name='t_orders'),
    path('item_logs/', include('items.item_logs.urls'), name='item_logs'),
    path('catalog/', include('orders.catalog.urls'), name='catalog'),
    path('orders/', include('orders.urls'), name='orders'),
    path('audit_form/', include('audit.form.urls'), name='audit_form'),
    path('audit_session/', include('audit.session.urls'), name='audit_session'),
    path('reports/', include('reports.urls'), name='reports'),

    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    # test mode
    from django.conf.urls.static import static

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
