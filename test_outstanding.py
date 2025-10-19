"""
Test script to verify outstanding balance calculation:
Current scenario:
- Bob has 2 payments for 2025-10: 200k and 200k (total 400k paid, 400k remaining)
- Alpha has 1 payment for 2025-10: 100k (200k remaining)
- Expected total outstanding: 400k + 200k = 600k (NOT 1,200k)
"""

import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Rental.settings')
django.setup()

from payments.models import Payment
from django.db.models import Sum

def test_outstanding_calculation():
    print("Testing Outstanding Balance Calculation")
    print("="*50)
    
    # Get all payments
    all_payments = Payment.objects.all().order_by('-payment_date', '-payment_id')
    
    print("Current Payments in System:")
    print("-"*30)
    for payment in all_payments:
        print(f"{payment.payment_id}: {payment.tenant.name} | "
              f"Paid: {payment.amount:,.0f} | Due: {payment.amount_due:,.0f} | "
              f"Period: {payment.rental_period} | Status: {payment.payment_status}")
    
    print("\n" + "="*50)
    print("CURRENT (WRONG) CALCULATION:")
    # Current wrong way - summing all amount_due values
    wrong_total = all_payments.filter(amount_due__gt=0).aggregate(
        Sum('amount_due')
    )['amount_due__sum'] or 0
    print(f"Sum of ALL amount_due values: UGX {wrong_total:,.0f}")
    
    print("\n" + "="*50)
    print("CORRECTED CALCULATION:")
    # Correct way - latest amount_due per tenant+rental+period
    outstanding_combinations = {}
    correct_total = 0
    
    for payment in all_payments:
        combo_key = (payment.tenant_id, payment.rental_id, payment.rental_period)
        
        if combo_key not in outstanding_combinations:
            outstanding_combinations[combo_key] = payment
            if payment.amount_due > 0:
                correct_total += payment.amount_due
                print(f"✓ {payment.tenant.name} ({payment.rental_period}): UGX {payment.amount_due:,.0f}")
    
    print(f"\nCORRECT Total Outstanding: UGX {correct_total:,.0f}")
    
    print("\n" + "="*50)
    print("VERIFICATION:")
    
    expected_total = 600000  # Bob: 400k + Alpha: 200k = 600k
    
    if correct_total == expected_total:
        print(f"✅ Outstanding calculation is CORRECT!")
        print(f"   Expected: UGX {expected_total:,.0f}")
        print(f"   Actual: UGX {correct_total:,.0f}")
    else:
        print(f"❌ Outstanding calculation is WRONG!")
        print(f"   Expected: UGX {expected_total:,.0f}")
        print(f"   Actual: UGX {correct_total:,.0f}")
    
    print(f"\nDifference from wrong method: UGX {wrong_total - correct_total:,.0f}")
    
    return correct_total == expected_total

if __name__ == "__main__":
    test_outstanding_calculation()