"""
Test script for Bob's CORRECTED payment scenario:
- Bob owes 800,000 UGX for monthly rent
- Bob pays 200,000 UGX 
- Expected Result: Amount Due should be 600,000 UGX (remaining balance)
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

def test_corrected_bob_scenario():
    print("Testing Bob's CORRECTED payment scenario...")
    print("="*60)
    
    # Find Bob
    try:
        bob = Tenant.objects.get(name__icontains='Bob')
        print(f"Found tenant: {bob.name}")
    except Tenant.DoesNotExist:
        print("❌ Bob not found. Please ensure Bob exists as a tenant.")
        return False
    except Tenant.MultipleObjectsReturned:
        bob = Tenant.objects.filter(name__icontains='Bob').first()
        print(f"Found multiple Bobs, using: {bob.name}")
    
    # Find Bob's rental
    try:
        rental = Rental.objects.filter(rental_tenants=bob).first()
        if not rental:
            print("❌ No rental found for Bob.")
            return False
        print(f"Found rental: {rental.rental_number}")
        print(f"Monthly rent amount: UGX {rental.monthly_rent_amount:,.2f}")
    except Exception as e:
        print(f"❌ Error finding rental: {e}")
        return False
    
    # Delete existing payments for clean test
    existing = Payment.objects.filter(tenant=bob, rental_period='2025-10')
    if existing.exists():
        print(f"Cleaning up {existing.count()} existing payments for Bob...")
        existing.delete()
    
    print("\n" + "-"*40)
    print("CREATING BOB'S PAYMENT")
    print("-"*40)
    
    # Create Bob's payment of 200,000 UGX
    payment = Payment.objects.create(
        tenant=bob,
        rental=rental,
        amount=200000.00,
        amount_due=800000.00,  # Will be updated by the system
        payment_date=date(2025, 10, 19),
        payment_method='CASH',
        rental_period='2025-10'
    )
    
    print(f"✓ Created payment: {payment.payment_id}")
    print(f"  Amount Paid: UGX {payment.amount:,.2f}")
    print(f"  Payment Date: {payment.payment_date}")
    print(f"  Rental Period: {payment.rental_period}")
    
    # Refresh payment from database to get updated values
    payment.refresh_from_db()
    
    print("\n" + "-"*40)
    print("VERIFICATION RESULTS")
    print("-"*40)
    
    # Test expectations
    expected_amount_due = 600000.00  # 800,000 - 200,000
    expected_status = 'PARTIAL'
    
    success = True
    
    print(f"Original Rent Amount: UGX {rental.monthly_rent_amount:,.2f}")
    print(f"Bob's Payment: UGX {payment.amount:,.2f}")
    print(f"Expected Amount Due: UGX {expected_amount_due:,.2f}")
    print(f"Actual Amount Due: UGX {payment.amount_due:,.2f}")
    
    if float(payment.amount_due) == expected_amount_due:
        print("✅ Amount Due is CORRECT!")
    else:
        print(f"❌ Amount Due is WRONG! Expected {expected_amount_due:,.2f}, Got {payment.amount_due:,.2f}")
        success = False
    
    # Test payment status
    actual_status = payment.payment_status
    print(f"Expected Status: {expected_status}")
    print(f"Actual Status: {actual_status}")
    
    if actual_status == expected_status:
        print("✅ Payment Status is CORRECT!")
    else:
        print(f"❌ Payment Status is WRONG! Expected {expected_status}, Got {actual_status}")
        success = False
    
    # Test payment summary
    print("\n" + "-"*40)
    print("PAYMENT SUMMARY TEST")
    print("-"*40)
    
    summary = Payment.get_payment_summary_for_tenant_rental(bob, rental, '2025-10')
    print(f"Total Paid: UGX {summary['total_paid']:,.2f}")
    print(f"Total Due: UGX {summary['total_due']:,.2f}")
    print(f"Remaining Balance: UGX {summary['remaining_balance']:,.2f}")
    print(f"Payment Count: {summary['payment_count']}")
    print(f"Status: {summary['status']}")
    
    if float(summary['remaining_balance']) == expected_amount_due:
        print("✅ Summary Remaining Balance is CORRECT!")
    else:
        print(f"❌ Summary Remaining Balance is WRONG!")
        success = False
    
    print("\n" + "="*60)
    if success:
        print("🎉 BOB'S CORRECTED PAYMENT SCENARIO TEST PASSED! 🎉")
        print("✅ 200k payment → 600k amount due ✅")
        print("The payment calculation logic is now working correctly!")
    else:
        print("❌ TEST FAILED - Payment calculation needs more fixes")
    
    return success

if __name__ == "__main__":
    test_corrected_bob_scenario()