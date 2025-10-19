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
    
    # Calculate enhanced statistics
    total_payments = payments.count()
    total_amount_paid = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Calculate outstanding amounts correctly - get latest amount_due per tenant+rental+period
    outstanding_combinations = {}
    total_outstanding = 0
    
    for payment in payments:
        # Create unique key for each tenant+rental+period combination
        combo_key = (payment.tenant_id, payment.rental_id, payment.rental_period)
        
        # Keep only the most recent payment for each combination (since payments are ordered by date desc)
        if combo_key not in outstanding_combinations:
            outstanding_combinations[combo_key] = payment
            # Only add to outstanding if there's still money due
            if payment.amount_due > 0:
                total_outstanding += payment.amount_due
    
    # Count payment statuses from the latest payments per combination
    paid_count = 0
    partial_count = 0
    unpaid_count = 0
    
    for payment in outstanding_combinations.values():
        status = payment.payment_status
        if status == 'PAID':
            paid_count += 1
        elif status == 'PARTIAL':
            partial_count += 1
        else:
            unpaid_count += 1
    
    # This month's payments
    today = timezone.now().date()
    first_day_of_month = today.replace(day=1)
    this_month_payments = payments.filter(
        payment_date__gte=first_day_of_month,
        payment_date__lte=today
    ).count()
    
    # Calculate completion rate based on payments with zero amount_due
    total_rental_periods = total_payments
    completion_rate = (paid_count / total_rental_periods * 100) if total_rental_periods > 0 else 0
    
    # Pagination
    paginator = Paginator(payments, 20)  # Show 20 payments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'payments': page_obj,
        'search_form': search_form,
        'total_payments': total_payments,
        'total_amount_paid': total_amount_paid,
        'total_amount_due': total_outstanding,  # Outstanding amounts
        'this_month_payments': this_month_payments,
        'paid_count': paid_count,
        'partial_count': partial_count,
        'unpaid_count': unpaid_count,
        'completion_rate': round(completion_rate, 1),
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
        
        # Get payment summary for this tenant/rental/period
        summary = Payment.get_payment_summary_for_tenant_rental(
            payment.tenant, payment.rental, payment.rental_period
        )
        
        data = {
            'payment_id': payment.payment_id,
            'tenant_name': payment.tenant.name,
            'property_name': payment.rental.property.property_name,
            'amount': float(payment.amount),
            'amount_due': float(payment.amount_due),
            'remaining_balance': float(summary['remaining_balance']),
            'total_paid': float(summary['total_paid']),
            'payment_status': summary['status'],
            'payment_date': payment.payment_date.isoformat(),
            'payment_method': payment.payment_method,
            'rental_period': payment.rental_period,
        }
        
        return JsonResponse(data)
    
    except Payment.DoesNotExist:
        return JsonResponse({'error': 'Payment not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def get_payment_info_ajax(request):
    """AJAX endpoint to get payment information for form auto-fill"""
    tenant_id = request.GET.get('tenant_id')
    rental_id = request.GET.get('rental_id')
    payment_date = request.GET.get('payment_date')
    
    if not all([tenant_id, rental_id, payment_date]):
        return JsonResponse({'error': 'Missing required parameters'}, status=400)
    
    try:
        from datetime import datetime
        tenant = get_object_or_404(Tenant, id=tenant_id)
        rental = get_object_or_404(Rental, id=rental_id)
        
        # Parse payment date and generate rental period
        payment_date_obj = datetime.strptime(payment_date, '%Y-%m-%d').date()
        rental_period = payment_date_obj.strftime('%Y-%m')
        
        # Get payment summary for this combination
        summary = Payment.get_payment_summary_for_tenant_rental(
            tenant, rental, rental_period
        )
        
        # If no previous payments for this period, use rental amount
        if summary['payment_count'] == 0:
            remaining_balance = float(rental.monthly_rent_amount)
        else:
            remaining_balance = float(summary['remaining_balance'])
        
        data = {
            'rental_period': rental_period,
            'remaining_balance': remaining_balance,
            'total_paid': float(summary['total_paid']),
            'payment_count': summary['payment_count'],
            'status': summary['status'],
            'monthly_rent': float(rental.monthly_rent_amount)
        }
        
        return JsonResponse(data)
        
    except (Tenant.DoesNotExist, Rental.DoesNotExist):
        return JsonResponse({'error': 'Tenant or Rental not found'}, status=404)
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def payment_receipt(request, payment_id):
    """Generate and display payment receipt"""
    try:
        payment = get_object_or_404(
            Payment.objects.select_related('tenant', 'rental__property'), 
            payment_id=payment_id
        )
        
        # Get payment summary for context
        try:
            summary = Payment.get_payment_summary_for_tenant_rental(
                payment.tenant, payment.rental, payment.rental_period
            )
        except Exception as summary_error:
            # If summary fails, create a basic one
            summary = {
                'total_due': payment.amount_due,
                'total_paid': payment.amount,
                'status': 'PAID' if payment.amount >= payment.amount_due else 'PARTIAL',
                'payment_count': 1
            }
        
        # Calculate remaining balance after this payment
        remaining_balance = max(0, payment.amount_due - payment.amount)
        
        context = {
            'payment': payment,
            'summary': summary,
            'remaining_balance': remaining_balance,
            'company_name': 'UNIHIVE RENTAL MANAGEMENT',
            'company_address': 'Kampala, Uganda',
            'company_phone': '+256 XXX XXX XXX',
            'company_email': 'info@unihive.com',
        }
        
        return render(request, 'payment_receipt.html', context)
        
    except Payment.DoesNotExist:
        return render(request, '404.html', {'message': 'Payment not found'})
    except Exception as e:
        # For debugging, let's also print the error
        print(f"Receipt view error for {payment_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        return render(request, '500.html', {'error': str(e)})
