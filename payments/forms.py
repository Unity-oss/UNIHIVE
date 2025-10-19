from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from .models import Payment
from tenants.models import Tenant
from rentals.models import Rental

class PaymentSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by payment ID, tenant name, or rental number...',
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'flex items-end space-x-2'
        self.helper.layout = Layout(
            Div(
                Field('search', css_class='w-full'),
                css_class='flex-1'
            ),
            Submit('submit', 'Search', css_class='bg-Unity-Purple hover:bg-Unity-purple2 text-white font-bold py-2 px-6 rounded-lg transition duration-200')
        )

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['tenant', 'rental', 'amount', 'amount_due', 'payment_date', 'payment_method', 'rental_period']
        widgets = {
            'tenant': forms.Select(attrs={
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5',
                'onchange': 'updatePaymentInfo()'
            }),
            'rental': forms.Select(attrs={
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5',
                'onchange': 'updatePaymentInfo()'
            }),
            'amount': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Enter payment amount',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'amount_due': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Amount due will be calculated automatically',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500 bg-gray-50',
                'readonly': True
            }),
            'payment_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5',
                'onchange': 'updatePaymentInfo()'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5'
            }),
            'rental_period': forms.TextInput(attrs={
                'placeholder': 'YYYY-MM (auto-filled from payment date)',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500',
                'readonly': True
            }),
        }
        labels = {
            'tenant': 'Tenant',
            'rental': 'Rental',
            'amount': 'Payment Amount (UGX)',
            'amount_due': 'Remaining Balance (UGX)',
            'payment_date': 'Payment Date',
            'payment_method': 'Payment Method',
            'rental_period': 'Rental Period',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure tenant dropdown
        self.fields['tenant'].queryset = Tenant.objects.all().order_by('name')
        self.fields['tenant'].empty_label = "Select a Tenant"
        
        # Configure rental dropdown
        self.fields['rental'].queryset = Rental.objects.all().order_by('rental_number')
        self.fields['rental'].empty_label = "Select a Rental"
        
        # Set default values for new payments
        if not self.instance.pk:  # Only for new payments
            if self.initial.get('payment_date'):
                # Auto-fill rental period from payment date
                payment_date = self.initial['payment_date']
                if hasattr(payment_date, 'strftime'):
                    self.initial['rental_period'] = payment_date.strftime('%Y-%m')
            
            # If tenant and rental are selected, calculate remaining balance
            if self.initial.get('tenant') and self.initial.get('rental'):
                tenant_id = self.initial['tenant']
                rental_id = self.initial['rental']
                rental_period = self.initial.get('rental_period')
                
                try:
                    tenant = Tenant.objects.get(id=tenant_id)
                    rental = Rental.objects.get(id=rental_id)
                    
                    # Get payment summary for this tenant/rental/period
                    summary = Payment.get_payment_summary_for_tenant_rental(
                        tenant, rental, rental_period
                    )
                    
                    # If no previous payments, use rental amount as amount due
                    if summary['payment_count'] == 0:
                        self.initial['amount_due'] = rental.monthly_rent_amount
                    else:
                        self.initial['amount_due'] = summary['remaining_balance']
                        
                except (Tenant.DoesNotExist, Rental.DoesNotExist):
                    pass