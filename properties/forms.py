from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Field
from .models import Property


class PropertySearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search by property ID, name, or address...',
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


class PropertyForm(forms.ModelForm):
    class Meta:
        model = Property
        fields = ['property_name', 'address']  # Removed property_id since it's auto-generated
        widgets = {
            'property_name': forms.TextInput(attrs={
                'placeholder': 'Enter property name',
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500'
            }),
            'address': forms.Textarea(attrs={
                'placeholder': 'Enter full property address',
                'rows': 3,
                'class': 'w-full pl-10 pr-3 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-Unity-Purple5 focus:border-Unity-Purple5 placeholder-gray-500 resize-vertical'
            }),
        }
        labels = {
            'property_name': 'Property Name',
            'address': 'Property Address',
        }
        error_messages = {
            'property_name': {
                'required': 'Please enter a property name. This field is required.',
                'max_length': 'Property name is too long. Please keep it under 15 characters.',
            },
            'address': {
                'required': 'Please enter the property address. This field is required.',
                'max_length': 'Address is too long. Please keep it under 15 characters.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Make all fields required
        for field_name, field in self.fields.items():
            field.required = True

    def clean_property_name(self):
        property_name = self.cleaned_data.get('property_name')
        if not property_name or not property_name.strip():
            raise forms.ValidationError('Property name cannot be empty or just spaces.')
        if len(property_name.strip()) < 2:
            raise forms.ValidationError('Property name must be at least 5 characters long.')
        return property_name.strip()

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if not address or not address.strip():
            raise forms.ValidationError('Property address cannot be empty or just spaces.')
        if len(address.strip()) < 10:
            raise forms.ValidationError('Please provide a complete address (at least 10 characters).')
        return address.strip()

    def clean(self):
        cleaned_data = super().clean()
        property_name = cleaned_data.get('property_name')
        address = cleaned_data.get('address')
        
        # Check if both fields are empty
        if not property_name and not address:
            raise forms.ValidationError('Please fill in all required fields to save the property.')
        
        return cleaned_data