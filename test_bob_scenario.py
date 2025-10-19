"""
Test script for Bob's payment scenario:
- Bob was initially charged 800,000 UGX 
- Bob paid 200,000 UGX yesterday (Oct 18, 2025)
- Bob paid 200,000 UGX today (Oct 19, 2025) 
- Bob paid 400,000 UGX again today (Oct 19, 2025)
- Total payments should be 800,000 UGX and status should be "PAID"
"""

import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rental.settings')
django.setup()

from payments.models import Payment
from tenants.models import Tenant
from rentals.models import Rental
from properties.models import Property

def create_bob_payment_scenario():
    print("Creating Bob's payment scenario...")
    
    # Find or create Bob as a tenant
    try:
        bob = Tenant.objects.get(name__icontains='Bob')
        print(f"Found existing tenant: {bob.name}")
    except Tenant.DoesNotExist:
        print("Bob not found. Please ensure Bob exists as a tenant in your system.")
        return
    except Tenant.MultipleObjectsReturned:
        bob = Tenant.objects.filter(name__icontains='Bob').first()
        print(f"Found multiple Bobs, using: {bob.name}")
    
    # Find Bob's rental
    try:
        rental = Rental.objects.filter(rental_tenants=bob).first()
        if not rental:
            print("No rental found for Bob. Please assign Bob to a rental.")
            return
        print(f"Found rental for Bob: {rental.rental_number}")
    except Exception as e:
        print(f"Error finding rental: {e}")
        return
    
    # Delete any existing payments for Bob this month to start fresh
    existing_payments = Payment.objects.filter(
        tenant=bob,
        rental=rental,
        rental_period='2025-10'
    )
    if existing_payments.exists():
        print(f"Deleting {existing_payments.count()} existing payments for Bob this month...")
        existing_payments.delete()
    
    # Create Bob's payment scenario
    print("\nCreating Bob's payments:")
    
    # Payment 1: 200,000 UGX on Oct 18, 2025 (yesterday)
    payment1 = Payment.objects.create(
        tenant=bob,
        rental=rental,
        amount=200000.00,
        amount_due=800000.00,  # Initial amount due
        payment_date=date(2025, 10, 18),
        payment_method='CASH',
        rental_period='2025-10'
    )
    print(f"✓ Payment 1: {payment1.payment_id} - UGX 200,000 (Oct 18)")
    
    # Payment 2: 200,000 UGX on Oct 19, 2025 (today)
    payment2 = Payment.objects.create(
        tenant=bob,
        rental=rental,
        amount=200000.00,
        amount_due=800000.00,  # Same period, will be updated by system
        payment_date=date(2025, 10, 19),
        payment_method='MOBILE',
        rental_period='2025-10'
    )
    print(f"✓ Payment 2: {payment2.payment_id} - UGX 200,000 (Oct 19)")
    
    # Payment 3: 400,000 UGX on Oct 19, 2025 (today - final payment)
    payment3 = Payment.objects.create(
        tenant=bob,
        rental=rental,
        amount=400000.00,
        amount_due=800000.00,  # Same period, will be updated by system
        payment_date=date(2025, 10, 19),
        payment_method='CARD',
        rental_period='2025-10'
    )
    print(f"✓ Payment 3: {payment3.payment_id} - UGX 400,000 (Oct 19)")
    
    # Test the aggregation system
    print("\n" + "="*60)
    print("TESTING PAYMENT AGGREGATION SYSTEM")
    print("="*60)
    
    summary = Payment.get_payment_summary_for_tenant_rental(
        bob, rental, '2025-10'
    )
    
    print(f"Tenant: {bob.name}")
    print(f"Rental: {rental.rental_number}")
    print(f"Period: 2025-10")
    print(f"Total Payments Made: UGX {summary['total_paid']:,.2f}")
    print(f"Original Amount Due: UGX {summary['total_due']:,.2f}")
    print(f"Remaining Balance: UGX {summary['remaining_balance']:,.2f}")
    print(f"Number of Payments: {summary['payment_count']}")
    print(f"Payment Status: {summary['status']}")
    
    # Check individual payment statuses
    print("\nIndividual Payment Details:")
    all_payments = Payment.objects.filter(
        tenant=bob,
        rental=rental,
        rental_period='2025-10'
    ).order_by('payment_date', 'id')
    
    for payment in all_payments:
        print(f"  {payment.payment_id}: UGX {payment.amount:,.2f} | "
              f"Due: UGX {payment.amount_due:,.2f} | "
              f"Status: {payment.payment_status} | "
              f"Date: {payment.payment_date}")
    
    # Verify the scenario
    print("\n" + "="*60)
    print("VERIFICATION")
    print("="*60)
    
    expected_total = 200000 + 200000 + 400000  # 800,000
    expected_status = 'PAID'
    expected_balance = 0
    
    success = True
    
    if summary['total_paid'] != expected_total:
        print(f"❌ Total payments mismatch: Expected {expected_total:,.2f}, Got {summary['total_paid']:,.2f}")
        success = False
    else:
        print(f"✅ Total payments correct: UGX {summary['total_paid']:,.2f}")
    
    if summary['status'] != expected_status:
        print(f"❌ Status mismatch: Expected {expected_status}, Got {summary['status']}")
        success = False
    else:
        print(f"✅ Payment status correct: {summary['status']}")
    
    if summary['remaining_balance'] != expected_balance:
        print(f"❌ Balance mismatch: Expected {expected_balance:,.2f}, Got {summary['remaining_balance']:,.2f}")
        success = False
    else:
        print(f"✅ Remaining balance correct: UGX {summary['remaining_balance']:,.2f}")
    
    if success:
        print("\n🎉 BOB'S PAYMENT SCENARIO TEST PASSED! 🎉")
        print("The payment aggregation system is working correctly!")
    else:
        print("\n❌ Test failed. Please check the implementation.")
    
    return success

if __name__ == "__main__":
    create_bob_payment_scenario()