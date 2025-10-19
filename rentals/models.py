from django.db import models
import re

# Create your models here.
RENTAL_TYPES = [
        ("SINGLE_ROOM", "Single Room"),
        ("DOUBLE_ROOM", "Double Room"),
        ("SHOP", "Shop"),
        ("APARTMENT", "Apartment"),
        ("HOUSE", "House"),
        ("STUDIO", "Studio"),
    ]


class Rental(models.Model):
    rental_number = models.CharField(max_length=20, unique=True, blank=True)
    rental_type = models.CharField(max_length=50, choices=RENTAL_TYPES)
    property = models.ForeignKey('properties.Property', on_delete=models.CASCADE)
    monthly_rent_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    def generate_property_prefix(self, property_name):
        """
        Generate a prefix from property name by taking the first 5-6 characters
        of significant words (excluding common words like 'estates', 'properties', etc.)
        """
        # Remove common property words and clean the name
        common_words = ['estates', 'properties', 'property', 'estate', 'homes', 'home', 'apartments', 'apartment']
        words = property_name.upper().split()
        
        # Filter out common words
        significant_words = [word for word in words if word.lower() not in common_words]
        
        if not significant_words:
            # If all words were filtered out, use the original words
            significant_words = words
        
        # Create prefix from the first significant word(s)
        if len(significant_words) == 1:
            # Single word: take first 5-6 characters
            prefix = significant_words[0][:6]
        else:
            # Multiple words: take first few characters from each
            prefix = ""
            for word in significant_words[:2]:  # Use first 2 significant words
                if len(prefix) < 4:
                    prefix += word[:3]
                else:
                    prefix += word[:2]
            prefix = prefix[:6]  # Limit to 6 characters
        
        # Remove any non-alphabetic characters
        prefix = re.sub(r'[^A-Z]', '', prefix)
        
        return prefix
    
    def save(self, *args, **kwargs):
        if not self.rental_number:
            # Generate rental number based on property name
            property_name = self.property.property_name
            prefix = self.generate_property_prefix(property_name)
            
            # Find the last rental number for this property
            existing_rentals = Rental.objects.filter(
                rental_number__startswith=prefix
            ).order_by('rental_number')
            
            if existing_rentals.exists():
                # Get the last rental number and extract the numeric part
                last_rental = existing_rentals.last()
                last_number_str = last_rental.rental_number[len(prefix):]
                try:
                    last_number = int(last_number_str)
                    new_number = last_number + 1
                except ValueError:
                    new_number = 1
            else:
                new_number = 1
            
            # Generate the new rental number
            self.rental_number = f"{prefix}{new_number:03d}"
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Rental {self.rental_number} - {self.rental_type}"