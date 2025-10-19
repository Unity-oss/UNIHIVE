from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from .models import Rental, RENTAL_TYPES
from properties.models import Property


class RentalSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by rental number, property name, or type...',
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


class RentalForm(forms.ModelForm):
    class Meta:
        model = Rental
        fields = ['rental_type', 'property', 'monthly_rent_amount']
        widgets = {
            'rental_type': forms.Select(attrs={
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5'
            }),
            'property': forms.Select(attrs={
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5'
            }),
            'monthly_rent_amount': forms.NumberInput(attrs={
                'placeholder': 'Enter monthly rent amount',
                'class': 'w-full pl-16 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500',
                'step': '0.01',
                'min': '0',
                'max': '99999999.99'
            }),
        }
        labels = {
            'rental_type': 'Rental Type',
            'property': 'Property',
            'monthly_rent_amount': 'Monthly Rent Amount (UGX)',
        }
        error_messages = {
            'rental_type': {
                'required': 'Please select a rental type. This field is required.',
            },
            'property': {
                'required': 'Please select a property. This field is required.',
            },
            'monthly_rent_amount': {
                'required': 'Please enter the monthly rent amount. This field is required.',
                'invalid': 'Please enter a valid amount (numbers only, with optional decimal places).',
                'min_value': 'Rent amount must be greater than 0.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True
        
        # Customize property queryset
        self.fields['property'].queryset = Property.objects.all()
        self.fields['property'].empty_label = "Select a Property"
        
        # Customize rental type
        self.fields['rental_type'].empty_label = "Select Rental Type"

    def clean_monthly_rent_amount(self):
        amount = self.cleaned_data.get('monthly_rent_amount')
        if amount is None:
            raise forms.ValidationError('Monthly rent amount is required.')
        if amount <= 0:  # Amount must be positive
            raise forms.ValidationError('Monthly rent amount must be greater than 0.')
        if amount < 100000:  # Minimum rent amount set to 100,000 UGX
            raise forms.ValidationError('Monthly rent amount must be at least 100,000 UGX.')
        if amount > 50000000:  # 50 million UGX seems reasonable as max
            raise forms.ValidationError('Monthly rent amount is too high. Please enter a reasonable amount.')
        return amount

    def clean_property(self):
        property_obj = self.cleaned_data.get('property')
        if not property_obj:
            raise forms.ValidationError('Please select a property from the list.')
        return property_obj

    def clean_rental_type(self):
        rental_type = self.cleaned_data.get('rental_type')
        if not rental_type:
            raise forms.ValidationError('Please select a rental type.')
        valid_types = [choice[0] for choice in RENTAL_TYPES]
        if rental_type not in valid_types:
            raise forms.ValidationError('Please select a valid rental type.')
        return rental_type

    def clean(self):
        cleaned_data = super().clean()
        property_obj = cleaned_data.get('property')
        rental_type = cleaned_data.get('rental_type')
        amount = cleaned_data.get('monthly_rent_amount')
        
        # Check if all required fields are filled
        if not all([property_obj, rental_type, amount]):
            raise forms.ValidationError('Please fill in all required fields to create the rental.')
        
        return cleaned_data