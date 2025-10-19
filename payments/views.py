from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Sum, Count
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.utils import timezone
from datetime import datetime, timedelta
from .models import Payment
from .forms import PaymentForm, PaymentSearchForm
from tenants.models import Tenant
from rentals.models import Rental

def payment_list(request):
    """Display paginated list of payments with search functionality"""
    search_form = PaymentSearchForm(request.GET)
    payments = Payment.objects.select_related('tenant', 'rental__property').all()
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        if search_query:
            payments = payments.filter(
                Q(payment_id__icontains=search_query) |
                Q(tenant__name__icontains=search_query) |
                Q(rental__rental_number__icontains=search_query) |
                Q(rental__property__property_name__icontains=search_query) |
                Q(payment_method__icontains=search_query)
            )
    
    # Order payments by most recent first
    payments = payments.order_by('-payment_date', '-payment_id')
    
    # Calculate statistics
    total_payments = payments.count()
    total_amount_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    total_amount_due = payments.aggregate(Sum('amount_due'))['amount_due__sum'] or 0
    
    # This month's payments
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    this_month_payments = payments.filter(
        payment_date__gte=first_day_of_month,
        payment_date__lte=today
    ).count()
    
    # Pagination
    paginator = Paginator(payments, 20)  # Show 20 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'search_form': search_form,
        'total_payments': total_payments,
        'total_amount_paid': total_amount_paid,
        'total_amount_due': total_amount_due,
        'this_month_payments': this_month_payments,
    }
    
    return render(request, 'paymentlist.html', context)

def add_payment(request):
    """Add a new payment"""
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save()
            messages.success(request, f'Payment {payment.payment_id} has been recorded successfully!')
            return redirect('payments:payment_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PaymentForm()
    
    context = {
        'form': form,
        'is_edit': False,
    }
    
    return render(request, 'paymentform.html', context)

def edit_payment(request, payment_id):
    """Edit an existing payment"""
    payment = get_object_or_404(Payment, payment_id=payment_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            updated_payment = form.save()
            messages.success(request, f'Payment {updated_payment.payment_id} has been updated successfully!')
            return redirect('payments:payment_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PaymentForm(instance=payment)
    
    context = {
        'form': form,
        'payment': payment,
        'is_edit': True,
    }
    
    return render(request, 'paymentform.html', context)

def delete_payment(request, payment_id):
    """Delete a payment"""
    payment = get_object_or_404(Payment, payment_id=payment_id)
    
    if request.method == 'POST':
        payment_ref = f'{payment.payment_id}'
        payment.delete()
        messages.success(request, f'Payment {payment_ref} has been deleted successfully!')
        return redirect('payments:payment_list')
    
    # If not POST, redirect back to list
    return redirect('payments:payment_list')

def get_payment_details(request, payment_id):
    """API endpoint to get payment details for modal view"""
    try:
        payment = get_object_or_404(
            Payment.objects.select_related('tenant', 'rental__property'), 
            payment_id=payment_id
        )
        
        # Calculate balance
        balance = payment.amount_due - payment.amount
        
        data = {
            'payment_id': payment.payment_id,
            'tenant_name': payment.tenant.name,
            'property_name': payment.rental.property.property_name,
            'amount': float(payment.amount),
            'amount_due': float(payment.amount_due),
            'balance': max(0, balance),  # Don't show negative balance
            'payment_date': payment.payment_date.isoformat(),
            'payment_method': payment.payment_method,
        }
        
        return JsonResponse(data)
    
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
