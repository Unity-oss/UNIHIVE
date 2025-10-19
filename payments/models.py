from django.db import models
from django.db.models import Sum, Q
from decimal import Decimal

# Create your models here.
PAYMENT_METHODS = [
        ("CASH", "Cash"),
        ("CARD", "Card"),
        ("MOBILE", "Mobile Money"),
    ]


class Payment(models.Model):
    payment_id = models.CharField(max_length=20, unique=True)
    rental = models.ForeignKey('rentals.Rental', on_delete=models.CASCADE)
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    rental_period = models.CharField(max_length=20, help_text="Format: YYYY-MM (e.g., 2025-10)", blank=True)

    def save(self, *args, **kwargs):
        if not self.payment_id:
            # Generate payment ID
            last_payment = Payment.objects.order_by('-id').first()
            if last_payment:
                last_id = int(last_payment.payment_id.replace('PAY-', '')) if last_payment.payment_id.startswith('PAY-') else 0
                new_id = last_id + 1
            else:
                new_id = 1
            self.payment_id = f'PAY-{new_id:04d}'
        
        # Auto-set rental period if not provided
        if not self.rental_period and self.payment_date:
            self.rental_period = self.payment_date.strftime('%Y-%m')
        
        super().save(*args, **kwargs)
        
        # After saving, update all related payments for this tenant+rental+period
        self.update_payment_balances()

    @classmethod
    def get_payment_summary_for_tenant_rental(cls, tenant, rental, rental_period=None):
        """
        Get payment summary for a specific tenant and rental combination.
        If rental_period is provided, filter by that period as well.
        Returns total paid, total due, and remaining balance.
        """
        payments_filter = Q(tenant=tenant, rental=rental)
        if rental_period:
            payments_filter &= Q(rental_period=rental_period)
        
        payments = cls.objects.filter(payments_filter)
        
        if not payments.exists():
            return {
                'total_paid': Decimal('0.00'),
                'total_due': rental.monthly_rent_amount,  # Use rental amount as base
                'remaining_balance': rental.monthly_rent_amount,
                'payment_count': 0,
                'status': 'UNPAID'
            }
        
        # Calculate total amount paid
        total_paid = payments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        # Use rental monthly amount as the total due for this period
        total_due = rental.monthly_rent_amount
        
        # Calculate remaining balance
        remaining_balance = max(Decimal('0.00'), total_due - total_paid)
        
        # Determine status
        if remaining_balance == Decimal('0.00') and total_paid > Decimal('0.00'):
            status = 'PAID'
        elif total_paid > Decimal('0.00'):
            status = 'PARTIAL'
        else:
            status = 'UNPAID'
        
        return {
            'total_paid': total_paid,
            'total_due': total_due,
            'remaining_balance': remaining_balance,
            'payment_count': payments.count(),
            'status': status
        }

    def update_payment_balances(self):
        """
        Update the amount_due field for all payments related to this tenant+rental+period
        Each payment should show the remaining balance AFTER that specific payment.
        """
        # Get all payments for this tenant+rental+period combination
        related_payments = Payment.objects.filter(
            tenant=self.tenant, 
            rental=self.rental,
            rental_period=self.rental_period
        ).order_by('payment_date', 'id')
        
        if not related_payments.exists():
            return
        
        # Get the original total amount due (should be the rental amount)
        # Use the rental's monthly rent as the base amount due
        original_amount_due = self.rental.monthly_rent_amount
        
        # Calculate running balances for each payment
        running_total_paid = Decimal('0.00')
        
        for payment in related_payments:
            running_total_paid += payment.amount
            remaining_balance = max(Decimal('0.00'), original_amount_due - running_total_paid)
            
            # Update this payment's amount_due to show remaining balance after this payment
            Payment.objects.filter(id=payment.id).update(
                amount_due=remaining_balance
            )

    @property
    def payment_status(self):
        """
        Calculate the payment status based on amount paid vs amount due for this rental period.
        """
        summary = self.get_payment_summary_for_tenant_rental(
            self.tenant, self.rental, self.rental_period
        )
        return summary['status']

    @property
    def remaining_balance(self):
        """
        Get the remaining balance for this tenant+rental+period combination.
        """
        summary = self.get_payment_summary_for_tenant_rental(
            self.tenant, self.rental, self.rental_period
        )
        return summary['remaining_balance']

    @property
    def total_paid_for_rental_period(self):
        """
        Get the total amount paid by this tenant for this rental in this period.
        """
        summary = self.get_payment_summary_for_tenant_rental(
            self.tenant, self.rental, self.rental_period
        )
        return summary['total_paid']

    def __str__(self):
        return f"Payment {self.tenant} of {self.amount}"