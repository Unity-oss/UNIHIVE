from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from datetime import timedelta
from .models import Tenant
from .forms import TenantForm, TenantSearchForm
from rentals.models import Rental

# Create your views here.

def tenant_list(request):
    """Enhanced tenant list view with search functionality"""
    # Get search query
    search_form = TenantSearchForm(request.GET)
    tenants = Tenant.objects.all().order_by('-move_in_date')
    
    # Apply search filter
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        if search_query:
            tenants = tenants.filter(
                Q(name__icontains=search_query) |
                Q(email__icontains=search_query) |
                Q(phone_number__icontains=search_query) |
                Q(nin_number__icontains=search_query) |
                Q(tenant_property__property_name__icontains=search_query) |
                Q(rental__rental_number__icontains=search_query)
            )
    
    # Calculate statistics
    today = timezone.now().date()
    overdue_count = 0
    due_soon_count = 0
    on_track_count = 0
    
    for tenant in tenants:
        if tenant.rent_due_date:
            if tenant.rent_due_date < today:
                overdue_count += 1
            elif tenant.rent_due_date <= today + timedelta(days=7):
                due_soon_count += 1
            else:
                on_track_count += 1
        else:
            on_track_count += 1
    
    return render(request, 'tenantList.html', {
        'search_form': search_form,
        'total_tenants': tenants.count(),
        'overdue_count': overdue_count,
        'due_soon_count': due_soon_count,
        'on_track_count': on_track_count,
        'tenants': tenants
    })

def tenant_create(request):
    """Create a new tenant"""
    if request.method == 'POST':
        form = TenantForm(request.POST)
        if form.is_valid():
            tenant = form.save()
            messages.success(request, f'Tenant "{tenant.name}" has been added successfully!')
            return redirect('tenants:tenant_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TenantForm()
    
    return render(request, 'tenantform.html', {
        'form': form,
        'is_edit': False
    })

def tenant_update(request, pk):
    """Update an existing tenant"""
    tenant = get_object_or_404(Tenant, pk=pk)
    
    if request.method == 'POST':
        form = TenantForm(request.POST, instance=tenant)
        if form.is_valid():
            tenant = form.save()
            messages.success(request, f'Tenant "{tenant.name}" has been updated successfully!')
            return redirect('tenants:tenant_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = TenantForm(instance=tenant)
    
    return render(request, 'tenantform.html', {
        'form': form,
        'is_edit': True,
        'tenant': tenant
    })

def tenant_delete(request, pk):
    """Delete a tenant"""
    tenant = get_object_or_404(Tenant, pk=pk)
    
    if request.method == 'POST':
        try:
            tenant_name = tenant.name
            tenant.delete()
            messages.success(
                request, 
                f'Tenant "{tenant_name}" has been deleted successfully!'
            )
        except Exception as e:
            messages.error(
                request, 
                f'An error occurred while deleting the tenant: {str(e)}'
            )
    
    return redirect('tenants:tenant_list')

def get_rental_details(request, rental_id):
    """API endpoint to get rental details for auto-updating form fields"""
    try:
        rental = get_object_or_404(Rental, pk=rental_id)
        data = {
            'property_id': rental.property.pk,
            'property_name': rental.property.property_name,
            'monthly_rent_amount': str(rental.monthly_rent_amount),
            'rental_type': rental.rental_type,
            'rental_number': rental.rental_number,
        }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
