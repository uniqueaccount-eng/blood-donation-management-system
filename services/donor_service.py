"""
services/donor_service.py
Service for registering donors, checking eligibility, and recording donation sessions.
"""
from datetime import date
from typing import List, Optional
from models.enums import BloodGroup, DonorStatus
from models.person import Donor
from models.request import DonationRecord
from models.blood_unit import BloodUnit
from storage.storage_interface import StorageProvider


class DonorService:
    """
    Handles donor management and records new donations.
    """

    def __init__(self, storage_provider: StorageProvider):
        self._storage = storage_provider
        self._donors: List[Donor] = self._storage.load_donors()
        self._donations: List[DonationRecord] = self._storage.load_donations()

    def register_donor(self, donor: Donor) -> Donor:
        """Registers a new donor ensuring ID uniqueness."""
        if any(d.id == donor.id for d in self._donors):
            raise ValueError(f"Donor with ID '{donor.id}' already exists.")
        self._donors.append(donor)
        self._storage.save_donors(self._donors)
        return donor

    def get_all_donors(self) -> List[Donor]:
        return list(self._donors)

    def get_donor_by_id(self, donor_id: str) -> Optional[Donor]:
        for d in self._donors:
            if d.id.strip().upper() == donor_id.strip().upper():
                return d
        return None

    def search_donors(
        self,
        query: str = "",
        blood_group: Optional[BloodGroup] = None,
        only_eligible: bool = False
    ) -> List[Donor]:
        """Filters donors by name/contact/city, blood group, and eligibility."""
        results = self._donors
        if query:
            q = query.lower().strip()
            results = [
                d for d in results
                if q in d.full_name.lower() or q in d.city.lower() or q in d.contact_number
            ]
        if blood_group is not None:
            results = [d for d in results if d.blood_group == blood_group]
        if only_eligible:
            results = [
                d for d in results
                if d.evaluate_eligibility()[0] == DonorStatus.ELIGIBLE
            ]
        return results

    def record_donation(
        self,
        donor_id: str,
        unit_id: str,
        donation_date: Optional[date] = None,
        facility: str = "Central Blood Bank"
    ) -> DonationRecord:
        """
        Processes a physical donation session:
        1. Checks eligibility.
        2. Updates donor last donation date and total count.
        3. Generates immutable DonationRecord audit log.
        """
        donor = self.get_donor_by_id(donor_id)
        if not donor:
            raise ValueError(f"Donor ID '{donor_id}' not found.")

        status, reason = donor.evaluate_eligibility()
        if status != DonorStatus.ELIGIBLE:
            raise ValueError(f"Donor is ineligible for donation: {reason}")

        d_date = donation_date or date.today()
        donor.record_new_donation(d_date)
        self._storage.save_donors(self._donors)

        record_id = f"DON-{len(self._donations) + 3001}"
        record = DonationRecord(
            record_id=record_id,
            donor_id=donor.id,
            donor_name=donor.full_name,
            blood_group=donor.blood_group,
            unit_id=unit_id,
            donation_date=d_date,
            camp_or_facility=facility
        )
        self._donations.append(record)
        self._storage.save_donations(self._donations)
        return record

    def get_all_donation_records(self) -> List[DonationRecord]:
        return list(self._donations)
