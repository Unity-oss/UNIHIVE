from django.contrib import admin
from .models import Tenant

# Register your models here.
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_number', 'move_in_date', 'rent_due_date', 'rent_amount']
    list_filter = ['move_in_date', 'tenant_property', 'rental']
    search_fields = ['name', 'email', 'nin_number']
    readonly_fields = ['rent_due_date']
    
    fieldsets = (
        ('Personal Information', {
            'fields': ('name', 'email', 'phone_number', 'nin_number')
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone')
        }),
        ('Rental Information', {
            'fields': ('rental', 'tenant_property', 'move_in_date', 'rent_due_date', 'rent_amount')
        }),
    )
    
    def rent_due_date(self, obj):
        """Display the calculated rent due date"""
        return obj.rent_due_date
    rent_due_date.short_description = 'Rent Due Date'