from django.contrib import admin
from django.urls import path

from Core.views import frontpage, dashboard, contact

urlpatterns = [
    path('', frontpage, name='frontpage'),
    path('dashboard/', dashboard, name='dashboard'),
    path('contact/', contact, name='contact'),
    path('admin/', admin.site.urls),
]
