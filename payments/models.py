from django.db import models

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
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.tenant} of {self.amount}"