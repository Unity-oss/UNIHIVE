from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from .models import Tenant
from rentals.models import Rental
from properties.models import Property

class TenantSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by name, email, phone, or NIN...',
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

class TenantForm(forms.ModelForm):
    class Meta:
        model = Tenant
        fields = ['name', 'email', 'phone_number', 'nin_number', 'emergency_contact_name', 
                 'emergency_contact_phone', 'rental', 'tenant_property', 'move_in_date', 'rent_amount']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': 'Enter tenant name',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Enter email address',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'phone_number': forms.TextInput(attrs={
                'placeholder': 'Enter phone number',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'nin_number': forms.TextInput(attrs={
                'placeholder': 'Enter NIN number',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'emergency_contact_name': forms.TextInput(attrs={
                'placeholder': 'Enter emergency contact name',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'placeholder': 'Enter emergency contact phone',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'move_in_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5'
            }),
            'rent_amount': forms.NumberInput(attrs={
                'step': '0.01',
                'placeholder': 'Enter rent amount',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'rental': forms.Select(attrs={
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5'
            }),
            'tenant_property': forms.Select(attrs={
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5'
            }),
        }
        labels = {
            'name': 'Tenant Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'nin_number': 'NIN Number',
            'emergency_contact_name': 'Emergency Contact Name',
            'emergency_contact_phone': 'Emergency Contact Phone',
            'rental': 'Rental',
            'tenant_property': 'Property',
            'move_in_date': 'Move-in Date',
            'rent_amount': 'Rent Amount (UGX)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configure rental dropdown to show available rentals
        self.fields['rental'].queryset = Rental.objects.all().order_by('rental_number')
        self.fields['rental'].empty_label = "Select a Rental First"
        
        # Configure property dropdown - will be auto-filled when rental is selected
        self.fields['tenant_property'].queryset = Property.objects.all().order_by('property_name')
        self.fields['tenant_property'].empty_label = "Will auto-fill when rental is selected"
        # Don't disable in Django form - handle via JavaScript instead
        
        # Configure rent amount field - will be auto-filled when rental is selected
        self.fields['rent_amount'].widget.attrs['placeholder'] = 'Will auto-fill when rental is selected'
        # Don't make readonly in Django form - handle via JavaScript instead