from django.db import models
from datetime import datetime
import calendar

# Create your models here.
class Tenant(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    nin_number = models.CharField(max_length=20, unique=True)
    emergency_contact_name = models.CharField(max_length=60)
    emergency_contact_phone = models.CharField(max_length=15)
    rental = models.ForeignKey('rentals.Rental', on_delete=models.CASCADE, related_name='rental_tenants')
    tenant_property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    move_in_date = models.DateField()    
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def rent_due_date(self):
        """Calculate rent due date as exactly 3 months from move_in_date"""
        if self.move_in_date:
            # Add 3 months to the move_in_date
            year = self.move_in_date.year
            month = self.move_in_date.month + 3
            day = self.move_in_date.day
            
            # Handle year overflow
            if month > 12:
                year += (month - 1) // 12
                month = ((month - 1) % 12) + 1
            
            # Handle day overflow for months with fewer days
            max_day = calendar.monthrange(year, month)[1]
            if day > max_day:
                day = max_day
                
            return datetime(year, month, day).date()
        return None

    def __str__(self):
        return f"{self.name} {self.rental}"
