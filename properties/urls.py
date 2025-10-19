from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('', views.property_list2, name='property_list'),
    path('addproperty/', views.add_property, name='add_property'),
    path('edit/<int:pk>/', views.edit_property, name='edit_property'),
    path('delete/<int:pk>/', views.delete_property, name='delete_property'),
]