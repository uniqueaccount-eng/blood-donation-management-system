"""
tests/test_oop_system.py
Unit tests for the Blood Donation Management System.
Tests inheritance, getters/setters validation, eligibility, and compatibility logic.
"""
import unittest
import os
import shutil
import tempfile
from datetime import date, timedelta, datetime

from models.enums import BloodGroup, BloodComponent, UnitStatus, DonorStatus, RequestUrgency, RequestStatus
from models.person import Person, Donor, Recipient, MedicalStaff
from models.blood_unit import BloodUnit, BloodUnitError
from models.request import BloodRequest, DonationRecord
from services.compatibility import BloodCompatibilityService, RedBloodCellCompatibilityStrategy, PlasmaCompatibilityStrategy
from services.inventory_manager import InventoryManager
from services.donor_service import DonorService
from services.request_service import RequestService
from storage.json_storage import JSONStorage


class TestOOPPrinciples(unittest.TestCase):
    """Verifies core OOP constraints and inheritance behavior."""

    def test_abstract_person_instantiation(self):
        """Abstraction: Abstract class Person cannot be directly instantiated."""
        with self.assertRaises(TypeError):
            Person("ID-01", "John", "Doe", BloodGroup.O_POS, "12345678", "j@e.com", 30, "Male")

    def test_encapsulation_and_setters(self):
        """Encapsulation: Property setters strictly validate data bounds."""
        donor = Donor(
            person_id="D-1",
            first_name="Alice",
            last_name="Smith",
            blood_group=BloodGroup.A_POS,
            contact_number="9876543210",
            email="alice@test.com",
            age=25,
            gender="Female",
            weight_kg=55.0
        )
        # Test valid mutation
        donor.age = 26
        self.assertEqual(donor.age, 26)

        # Test invalid age (encapsulation prevents corruption)
        with self.assertRaises(ValueError):
            donor.age = -5
        with self.assertRaises(ValueError):
            donor.age = 150

        # Test invalid weight
        with self.assertRaises(ValueError):
            donor.weight_kg = 0

    def test_donor_clinical_eligibility(self):
        """Domain Logic: Testing clinical criteria (age, weight, cooldown)."""
        today = date.today()

        # Underweight donor (<50kg)
        donor_light = Donor(
            person_id="D-2", first_name="Bob", last_name="Lee",
            blood_group=BloodGroup.B_POS, contact_number="1234567890", email="b@t.com",
            age=22, gender="Male", weight_kg=47.0
        )
        status, reason = donor_light.evaluate_eligibility()
        self.assertEqual(status, DonorStatus.TEMPORARY_DEFERRAL)
        self.assertIn("Underweight", reason)

        # Donor within 90-day cooldown period
        donor_recent = Donor(
            person_id="D-3", first_name="Charlie", last_name="Brown",
            blood_group=BloodGroup.O_POS, contact_number="1234567890", email="c@t.com",
            age=30, gender="Male", weight_kg=70.0,
            last_donation_date=today - timedelta(days=40)
        )
        status, reason = donor_recent.evaluate_eligibility()
        self.assertEqual(status, DonorStatus.TEMPORARY_DEFERRAL)
        self.assertIn("Cooldown", reason)

        # Fully eligible donor
        donor_ok = Donor(
            person_id="D-4", first_name="Diana", last_name="Prince",
            blood_group=BloodGroup.O_NEG, contact_number="1234567890", email="d@t.com",
            age=28, gender="Female", weight_kg=60.0,
            last_donation_date=today - timedelta(days=100)
        )
        status, reason = donor_ok.evaluate_eligibility()
        self.assertEqual(status, DonorStatus.ELIGIBLE)

    def test_polymorphic_role_descriptions(self):
        """Polymorphism: Overridden method behaves differently per subclass."""
        d = Donor("D-1", "A", "B", BloodGroup.O_POS, "12345678", "a@b.com", 25, "M", 60.0)
        r = Recipient("R-1", "C", "D", BloodGroup.A_POS, "12345678", "c@d.com", 45, "F", "City Clinic")
        s = MedicalStaff("S-1", "E", "F", BloodGroup.B_NEG, "12345678", "e@f.com", 38, "F", "LIC-9988")

        self.assertIn("Blood Donor", d.get_role_description())
        self.assertIn("Recipient Patient", r.get_role_description())
        self.assertIn("Staff", s.get_role_description())


class TestCompatibilityStrategy(unittest.TestCase):
    """Verifies Strategy Pattern for blood compatibility."""

    def setUp(self):
        self.service = BloodCompatibilityService()

    def test_universal_donor_o_negative(self):
        """O- Red Blood Cells can be safely transfused to all 8 blood groups."""
        for recipient_bg in BloodGroup:
            is_compat = self.service.check_compatibility(
                donor_group=BloodGroup.O_NEG,
                recipient_group=recipient_bg,
                component=BloodComponent.WHOLE_BLOOD
            )
            self.assertTrue(is_compat, f"O- must be compatible with {recipient_bg.value}")

    def test_universal_recipient_ab_positive(self):
        """AB+ patient can receive RBCs from all 8 blood groups."""
        for donor_bg in BloodGroup:
            is_compat = self.service.check_compatibility(
                donor_group=donor_bg,
                recipient_group=BloodGroup.AB_POS,
                component=BloodComponent.WHOLE_BLOOD
            )
            self.assertTrue(is_compat, f"{donor_bg.value} must be able to donate to AB+")

    def test_incompatible_transfusions(self):
        """A+ cannot donate RBCs to B+, O+, or O-."""
        self.assertFalse(self.service.check_compatibility(BloodGroup.A_POS, BloodGroup.B_POS))
        self.assertFalse(self.service.check_compatibility(BloodGroup.A_POS, BloodGroup.O_POS))
        self.assertFalse(self.service.check_compatibility(BloodGroup.B_POS, BloodGroup.A_NEG))


class TestInventoryAndLifecycle(unittest.TestCase):
    """Verifies FIFO scheduling, expiration detection, and end-to-end fulfillment."""

    def setUp(self):
        InventoryManager.reset_instance()
        self.temp_dir = tempfile.mkdtemp()
        self.storage = JSONStorage(self.temp_dir)
        # Clear default seeds for controlled test
        self.storage.save_inventory([])
        self.storage.save_requests([])
        self.inventory = InventoryManager(self.storage)
        self.inventory._units = []
        self.compat = BloodCompatibilityService()
        self.request_svc = RequestService(self.storage, self.inventory, self.compat)

    def tearDown(self):
        InventoryManager.reset_instance()
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_fifo_earliest_expiry_allocation(self):
        """FIFO verification: unit with nearest expiry date is dispatched first."""
        today = date.today()

        # Add unit expiring in 20 days
        unit_later = BloodUnit(
            unit_id="U-LATER",
            blood_group=BloodGroup.A_POS,
            donor_id="D-1",
            collected_date=today - timedelta(days=15),
            expiry_date=today + timedelta(days=20),
            status=UnitStatus.AVAILABLE
        )
        # Add unit expiring in 5 days
        unit_sooner = BloodUnit(
            unit_id="U-SOONER",
            blood_group=BloodGroup.A_POS,
            donor_id="D-2",
            collected_date=today - timedelta(days=30),
            expiry_date=today + timedelta(days=5),
            status=UnitStatus.AVAILABLE
        )

        self.inventory.add_unit(unit_later)
        self.inventory.add_unit(unit_sooner)

        # Allocate 1 unit
        allocated = self.inventory.allocate_units_fifo(
            allowed_blood_groups=[BloodGroup.A_POS],
            units_needed=1
        )
        self.assertEqual(len(allocated), 1)
        self.assertEqual(allocated[0].unit_id, "U-SOONER", "FIFO must prioritize nearest expiry")

    def test_automated_expiry_detection(self):
        """Expired units are marked EXPIRED and excluded from available pool."""
        today = date.today()
        unit_old = BloodUnit(
            unit_id="U-EXPIRED",
            blood_group=BloodGroup.O_POS,
            donor_id="D-1",
            collected_date=today - timedelta(days=50),
            expiry_date=today - timedelta(days=10),
            status=UnitStatus.AVAILABLE
        )
        self.inventory.add_unit(unit_old)

        avail = self.inventory.get_available_units(BloodGroup.O_POS)
        self.assertEqual(len(avail), 0, "Expired unit must not appear in available inventory")
        self.assertEqual(unit_old.status, UnitStatus.EXPIRED)


if __name__ == "__main__":
    unittest.main()
