"""
storage/json_storage.py
Concrete implementation of StorageProvider using JSON files.
Includes automated initial data seeding with realistic clinical scenarios.
"""
import os
import json
from datetime import date, timedelta, datetime
from typing import List
from models.enums import BloodGroup, BloodComponent, UnitStatus, RequestUrgency, RequestStatus
from models.person import Donor, Recipient
from models.blood_unit import BloodUnit
from models.request import BloodRequest, DonationRecord
from storage.storage_interface import StorageProvider


class JSONStorage(StorageProvider):
    """
    Manages structured file persistence in JSON format.
    Automatically initializes default clinical demonstration data on first run.
    """

    def __init__(self, data_dir: str):
        self._data_dir = data_dir
        os.makedirs(self._data_dir, exist_ok=True)
        self._donors_file = os.path.join(self._data_dir, "donors.json")
        self._inventory_file = os.path.join(self._data_dir, "inventory.json")
        self._requests_file = os.path.join(self._data_dir, "requests.json")
        self._donations_file = os.path.join(self._data_dir, "donations.json")
        self._ensure_seed_data()

    def _ensure_seed_data(self):
        """Generates realistic seed dataset if files are missing or empty."""
        if not os.path.exists(self._donors_file):
            self._seed_default_data()

    def _seed_default_data(self):
        today = date.today()

        # Seed Donors
        seed_donors = [
            Donor(
                person_id="DNR-1001",
                first_name="Aarav",
                last_name="Sharma",
                blood_group=BloodGroup.O_NEG,
                contact_number="+91-98765-43210",
                email="aarav.sharma@example.org",
                age=28,
                gender="Male",
                weight_kg=68.5,
                last_donation_date=today - timedelta(days=110),
                total_donations=4,
                medical_conditions="None",
                city="Mumbai"
            ),
            Donor(
                person_id="DNR-1002",
                first_name="Priya",
                last_name="Verma",
                blood_group=BloodGroup.A_POS,
                contact_number="+91-98111-22334",
                email="priya.verma@example.org",
                age=24,
                gender="Female",
                weight_kg=56.0,
                last_donation_date=today - timedelta(days=30),  # Under 90-day cooldown
                total_donations=2,
                medical_conditions="None",
                city="Pune"
            ),
            Donor(
                person_id="DNR-1003",
                first_name="Rohan",
                last_name="Deshmukh",
                blood_group=BloodGroup.B_POS,
                contact_number="+91-99222-33445",
                email="rohan.deshmukh@example.org",
                age=35,
                gender="Male",
                weight_kg=74.0,
                last_donation_date=today - timedelta(days=95),
                total_donations=6,
                medical_conditions="None",
                city="Nashik"
            ),
            Donor(
                person_id="DNR-1004",
                first_name="Ananya",
                last_name="Iyer",
                blood_group=BloodGroup.AB_POS,
                contact_number="+91-97333-44556",
                email="ananya.iyer@example.org",
                age=22,
                gender="Female",
                weight_kg=48.0,  # Under 50kg limit
                last_donation_date=None,
                total_donations=0,
                medical_conditions="Mild seasonal allergies",
                city="Mumbai"
            ),
            Donor(
                person_id="DNR-1005",
                first_name="Vikram",
                last_name="Malhotra",
                blood_group=BloodGroup.O_POS,
                contact_number="+91-98444-55667",
                email="vikram.malhotra@example.org",
                age=31,
                gender="Male",
                weight_kg=78.0,
                last_donation_date=today - timedelta(days=120),
                total_donations=5,
                medical_conditions="None",
                city="Thane"
            ),
            Donor(
                person_id="DNR-1006",
                first_name="Sara",
                last_name="Khan",
                blood_group=BloodGroup.AB_NEG,
                contact_number="+91-96555-66778",
                email="sara.khan@example.org",
                age=29,
                gender="Female",
                weight_kg=62.0,
                last_donation_date=today - timedelta(days=100),
                total_donations=3,
                medical_conditions="None",
                city="Navi Mumbai"
            )
        ]
        self.save_donors(seed_donors)

        # Seed Inventory Units
        seed_units = [
            BloodUnit(
                unit_id="UNT-5001",
                blood_group=BloodGroup.O_NEG,
                donor_id="DNR-1001",
                component_type=BloodComponent.WHOLE_BLOOD,
                volume_ml=450.0,
                collected_date=today - timedelta(days=10),
                status=UnitStatus.AVAILABLE,
                storage_location="Vault Alpha - Shelf 1"
            ),
            BloodUnit(
                unit_id="UNT-5002",
                blood_group=BloodGroup.A_POS,
                donor_id="DNR-1002",
                component_type=BloodComponent.RED_BLOOD_CELLS,
                volume_ml=300.0,
                collected_date=today - timedelta(days=5),
                status=UnitStatus.AVAILABLE,
                storage_location="Vault Alpha - Shelf 2"
            ),
            BloodUnit(
                unit_id="UNT-5003",
                blood_group=BloodGroup.B_POS,
                donor_id="DNR-1003",
                component_type=BloodComponent.WHOLE_BLOOD,
                volume_ml=450.0,
                collected_date=today - timedelta(days=33),  # Expiring in 2 days
                status=UnitStatus.AVAILABLE,
                storage_location="Vault Alpha - Shelf 3"
            ),
            BloodUnit(
                unit_id="UNT-5004",
                blood_group=BloodGroup.O_POS,
                donor_id="DNR-1005",
                component_type=BloodComponent.PLATELETS,
                volume_ml=250.0,
                collected_date=today - timedelta(days=2),  # Expiring in 3 days
                status=UnitStatus.AVAILABLE,
                storage_location="Agitator Tray B"
            ),
            BloodUnit(
                unit_id="UNT-5005",
                blood_group=BloodGroup.AB_NEG,
                donor_id="DNR-1006",
                component_type=BloodComponent.PLASMA,
                volume_ml=300.0,
                collected_date=today - timedelta(days=40),
                status=UnitStatus.AVAILABLE,
                storage_location="Deep Freezer -20C"
            ),
            BloodUnit(
                unit_id="UNT-5006",
                blood_group=BloodGroup.O_POS,
                donor_id="DNR-1005",
                component_type=BloodComponent.WHOLE_BLOOD,
                volume_ml=450.0,
                collected_date=today - timedelta(days=40),  # Expired (35 days lifespan)
                status=UnitStatus.EXPIRED,
                storage_location="Vault Beta (Disposal Bin)"
            )
        ]
        self.save_inventory(seed_units)

        # Seed Requests
        seed_requests = [
            BloodRequest(
                request_id="REQ-8001",
                recipient_id="RCP-2001",
                recipient_name="Sunil Mehta",
                blood_group=BloodGroup.O_NEG,
                units_requested=1,
                hospital_name="Apex Trauma Center",
                urgency=RequestUrgency.CRITICAL,
                component_type=BloodComponent.WHOLE_BLOOD,
                request_date=datetime.now() - timedelta(hours=2),
                status=RequestStatus.PENDING,
                notes="Emergency trauma surgery scheduled."
            ),
            BloodRequest(
                request_id="REQ-8002",
                recipient_id="RCP-2002",
                recipient_name="Kavita Rane",
                blood_group=BloodGroup.B_POS,
                units_requested=2,
                hospital_name="City Memorial Hospital",
                urgency=RequestUrgency.URGENT,
                component_type=BloodComponent.WHOLE_BLOOD,
                request_date=datetime.now() - timedelta(hours=8),
                status=RequestStatus.PENDING,
                notes="Chemotherapy supportive transfusion."
            )
        ]
        self.save_requests(seed_requests)

        # Seed Donations Record
        seed_donations = [
            DonationRecord(
                record_id="DON-3001",
                donor_id="DNR-1001",
                donor_name="Aarav Sharma",
                blood_group=BloodGroup.O_NEG,
                unit_id="UNT-5001",
                donation_date=today - timedelta(days=10),
                camp_or_facility="Community Blood Drive #4"
            )
        ]
        self.save_donations(seed_donations)

    # --- Concrete Storage Implementations ---

    def load_donors(self) -> List[Donor]:
        if not os.path.exists(self._donors_file):
            return []
        try:
            with open(self._donors_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [Donor.from_dict(item) for item in data]
        except Exception:
            return []

    def save_donors(self, donors: List[Donor]) -> None:
        os.makedirs(self._data_dir, exist_ok=True)
        data = [d.to_dict() for d in donors]
        with open(self._donors_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_inventory(self) -> List[BloodUnit]:
        if not os.path.exists(self._inventory_file):
            return []
        try:
            with open(self._inventory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                units = [BloodUnit.from_dict(item) for item in data]
                # Auto-update any unit whose expiry date has passed
                changed = False
                for u in units:
                    if u.check_and_update_expiry():
                        changed = True
                if changed:
                    self.save_inventory(units)
                return units
        except Exception:
            return []

    def save_inventory(self, units: List[BloodUnit]) -> None:
        os.makedirs(self._data_dir, exist_ok=True)
        data = [u.to_dict() for u in units]
        with open(self._inventory_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_requests(self) -> List[BloodRequest]:
        if not os.path.exists(self._requests_file):
            return []
        try:
            with open(self._requests_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [BloodRequest.from_dict(item) for item in data]
        except Exception:
            return []

    def save_requests(self, requests: List[BloodRequest]) -> None:
        os.makedirs(self._data_dir, exist_ok=True)
        data = [r.to_dict() for r in requests]
        with open(self._requests_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load_donations(self) -> List[DonationRecord]:
        if not os.path.exists(self._donations_file):
            return []
        try:
            with open(self._donations_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [DonationRecord.from_dict(item) for item in data]
        except Exception:
            return []

    def save_donations(self, donations: List[DonationRecord]) -> None:
        os.makedirs(self._data_dir, exist_ok=True)
        data = [d.to_dict() for d in donations]
        with open(self._donations_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
