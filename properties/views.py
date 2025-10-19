from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from .forms import PropertyForm, PropertySearchForm
from .models import Property

# Create your views here.

@require_http_methods(["GET", "POST"])
def add_property(request):
    """
    View for adding a new property
    """
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        if form.is_valid():
            property_instance = form.save()
            messages.success(request, f'Property "{property_instance.property_name}" (ID: {property_instance.property_id}) has been added successfully!')
            return redirect('properties:property_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PropertyForm()
    
    return render(request, 'property_form.html', {'form': form})


@require_http_methods(["POST"])
def edit_property(request, pk):
    """
    View for editing an existing property via modal
    """
    property_instance = get_object_or_404(Property, pk=pk)
    
    if request.method == 'POST':
        property_name = request.POST.get('property_name')
        address = request.POST.get('address')
        
        if property_name and address:
            try:
                property_instance.property_name = property_name
                property_instance.address = address
                property_instance.save()
                messages.success(request, f'Property "{property_instance.property_name}" has been updated successfully!')
            except Exception as e:
                messages.error(request, f'Error updating property: {str(e)}')
        else:
            messages.error(request, 'Property name and address are required.')
    
    return redirect('properties:property_list')


@require_http_methods(["POST"])
def delete_property(request, pk):
    """
    View for deleting a property
    """
    property_instance = get_object_or_404(Property, pk=pk)
    property_name = property_instance.property_name
    property_instance.delete()
    messages.success(request, f'Property "{property_name}" has been deleted successfully!')
    return redirect('properties:property_list')


def property_list2(request):
    """
    Enhanced property list view with tables, search, and pagination
    """
    # Get search query
    search_form = PropertySearchForm(request.GET)
    properties = Property.objects.all()
    
    # Apply search filter
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        if search_query:
            properties = properties.filter(
                Q(property_id__icontains=search_query) |
                Q(property_name__icontains=search_query) |
                Q(address__icontains=search_query)
            )
    
    # Create table (simplified without django-tables2 for now)
    return render(request, 'property_list2.html', {
        'search_form': search_form,
        'total_properties': properties.count(),
        'properties': properties
    })
