from django.db import models

# Create your models here.
class Property(models.Model):
    property_id = models.CharField(max_length=20, unique=True, blank=True)
    property_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)

    def save(self, *args, **kwargs):
        if not self.property_id:
            # Auto-generate property_id
            last_property = Property.objects.all().order_by('id').last()
            if last_property:
                last_number = int(last_property.property_id.replace('PROP', ''))
                new_number = last_number + 1
            else:
                new_number = 1
            self.property_id = f'PROP{new_number:03d}'  # Format: PROP001, PROP002, etc.
        super().save(*args, **kwargs)

    def __str__(self):
        return self.property_name