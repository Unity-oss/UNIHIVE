from django.urls import path
from . import views

app_name = 'tenants'

urlpatterns = [
    path('', views.tenant_list, name='tenant_list'),
    path('create/', views.tenant_create, name='tenant_create'),
    path('<int:pk>/edit/', views.tenant_update, name='tenant_update'),
    path('<int:pk>/delete/', views.tenant_delete, name='tenant_delete'),
    path('api/rental/<int:rental_id>/', views.get_rental_details, name='get_rental_details'),
]