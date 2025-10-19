from django.urls import path
from . import views

app_name = 'rentals'

urlpatterns = [
    path('', views.rental_list, name='rental_list'),
    path('create/', views.rental_create, name='rental_create'),
    path('<int:pk>/edit/', views.rental_edit, name='rental_edit'),
    path('<int:pk>/', views.rental_detail, name='rental_detail'),
    path('<int:pk>/delete/', views.rental_delete, name='rental_delete'),
]