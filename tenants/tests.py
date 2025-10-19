from django.test import TestCase
from datetime import datetime, date
from .models import Tenant
from properties.models import Property
from rentals.models import Rental

# Create your tests here.

class TenantModelTest(TestCase):
    def setUp(self):
        # You'll need to create these if they don't exist
        # For now, we'll mock the basic structure
        pass
    
    def test_rent_due_date_calculation(self):
        """Test that rent_due_date is calculated correctly as 3 months from move_in_date"""
        # Create a tenant with a specific move-in date
        move_in_date = date(2024, 1, 15)  # January 15, 2024
        
        # Mock tenant (you'll need to adjust based on your actual model relationships)
        tenant = Tenant(
            name="Test Tenant",
            email="test@example.com",
            phone_number="1234567890",
            nin_number="TEST123456",
            emergency_contact_name="Emergency Contact",
            emergency_contact_phone="0987654321",
            move_in_date=move_in_date,
            rent_amount=500000.00
        )
        
        # Test the calculated rent due date
        expected_due_date = date(2024, 4, 15)  # 3 months later: April 15, 2024
        self.assertEqual(tenant.rent_due_date, expected_due_date)
    
    def test_rent_due_date_with_month_overflow(self):
        """Test rent due date calculation when months overflow (e.g., October + 3 months = January next year)"""
        move_in_date = date(2024, 10, 15)  # October 15, 2024
        
        tenant = Tenant(
            name="Test Tenant 2",
            email="test2@example.com",
            phone_number="1234567891",
            nin_number="TEST123457",
            emergency_contact_name="Emergency Contact 2",
            emergency_contact_phone="0987654322",
            move_in_date=move_in_date,
            rent_amount=600000.00
        )
        
        expected_due_date = date(2025, 1, 15)  # January 15, 2025
        self.assertEqual(tenant.rent_due_date, expected_due_date)
    
    def test_rent_due_date_with_day_adjustment(self):
        """Test rent due date calculation when the target month has fewer days"""
        move_in_date = date(2024, 1, 31)  # January 31, 2024
        
        tenant = Tenant(
            name="Test Tenant 3",
            email="test3@example.com",
            phone_number="1234567892",
            nin_number="TEST123458",
            emergency_contact_name="Emergency Contact 3",
            emergency_contact_phone="0987654323",
            move_in_date=move_in_date,
            rent_amount=700000.00
        )
        
        # April 31 doesn't exist, so it should be April 30
        expected_due_date = date(2024, 4, 30)  # April 30, 2024
        self.assertEqual(tenant.rent_due_date, expected_due_date)
    
    def test_rent_due_date_none_when_no_move_in_date(self):
        """Test that rent_due_date returns None when move_in_date is None"""
        tenant = Tenant(
            name="Test Tenant 4",
            email="test4@example.com",
            phone_number="1234567893",
            nin_number="TEST123459",
            emergency_contact_name="Emergency Contact 4",
            emergency_contact_phone="0987654324",
            move_in_date=None,
            rent_amount=800000.00
        )
        
        self.assertIsNone(tenant.rent_due_date)
