from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.db import transaction
from django.db import models
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from .models import Rental
from .forms import RentalForm, RentalSearchForm


def rental_list(request):
    """Display list of all rentals with search functionality"""
    form = RentalSearchForm(request.GET)
    rentals = Rental.objects.select_related('property').prefetch_related('rental_tenants').all().order_by('-id')
    
    if form.is_valid():
        search_query = form.cleaned_data.get('search')
        if search_query:
            rentals = rentals.filter(
                models.Q(rental_number__icontains=search_query) |
                models.Q(property__property_name__icontains=search_query) |
                models.Q(rental_type__icontains=search_query)
            )
    
    # Calculate statistics
    total_rentals = rentals.count()
    total_monthly_revenue = rentals.aggregate(total=Sum('monthly_rent_amount'))['total'] or 0
    unique_properties_count = rentals.values('property').distinct().count()
    
    # Pagination
    paginator = Paginator(rentals, 10)  # Show 10 rentals per page
    page_number = request.GET.get('page')
    rentals_page = paginator.get_page(page_number)
    
    context = {
        'rentals': rentals_page,
        'search_form': form,
        'total_rentals': total_rentals,
        'total_monthly_revenue': total_monthly_revenue,
        'unique_properties_count': unique_properties_count,
    }
    return render(request, 'rentalslist.html', context)


def rental_create(request):
    """Create a new rental"""
    if request.method == 'POST':
        form = RentalForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    rental = form.save()
                    messages.success(
                        request, 
                        f'Rental {rental.rental_number} has been created successfully! '
                        f'Property: {rental.property.property_name}, Type: {rental.get_rental_type_display()}'
                    )
                    return redirect('rentals:rental_list')
            except Exception as e:
                messages.error(
                    request, 
                    f'An error occurred while creating the rental: {str(e)}'
                )
        else:
            messages.error(
                request, 
                'Please correct the errors below and try again.'
            )
    else:
        form = RentalForm()
    
    context = {
        'form': form,
        'is_edit': False,
    }
    return render(request, 'rentalform.html', context)


def rental_edit(request, pk):
    """Edit an existing rental"""
    rental = get_object_or_404(Rental, pk=pk)
    
    if request.method == 'POST':
        form = RentalForm(request.POST, instance=rental)
        if form.is_valid():
            try:
                with transaction.atomic():
                    updated_rental = form.save()
                    messages.success(
                        request, 
                        f'Rental {updated_rental.rental_number} has been updated successfully!'
                    )
                    return redirect('rentals:rental_list')
            except Exception as e:
                messages.error(
                    request, 
                    f'An error occurred while updating the rental: {str(e)}'
                )
        else:
            messages.error(
                request, 
                'Please correct the errors below and try again.'
            )
    else:
        form = RentalForm(instance=rental)
    
    context = {
        'form': form,
        'rental': rental,
        'is_edit': True,
    }
    return render(request, 'rentalform.html', context)


def rental_detail(request, pk):
    """Display rental details"""
    rental = get_object_or_404(Rental, pk=pk)
    
    context = {
        'rental': rental,
    }
    return render(request, 'rental_detail.html', context)


def rental_delete(request, pk):
    """Delete a rental"""
    rental = get_object_or_404(Rental, pk=pk)
    
    if request.method == 'POST':
        try:
            rental_number = rental.rental_number
            property_name = rental.property.property_name
            rental.delete()
            messages.success(
                request, 
                f'Rental {rental_number} at {property_name} has been deleted successfully!'
            )
        except Exception as e:
            messages.error(
                request, 
                f'An error occurred while deleting the rental: {str(e)}'
            )
    
    return redirect('rentals:rental_list')
