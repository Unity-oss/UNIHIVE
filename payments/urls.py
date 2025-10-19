from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payment management URLs
    path('', views.payment_list, name='payment_list'),
    path('add/', views.add_payment, name='add_payment'),
    path('edit/<str:payment_id>/', views.edit_payment, name='edit_payment'),
    path('delete/<str:payment_id>/', views.delete_payment, name='delete_payment'),
    
    # API endpoints
    path('api/payment/<str:payment_id>/', views.get_payment_details, name='payment_details_api'),
]