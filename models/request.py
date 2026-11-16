"""
models/request.py
Classes for hospital blood requests and donation session records.
"""
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from models.enums import BloodGroup, BloodComponent, RequestUrgency, RequestStatus


class BloodRequest:
    """
    Represents a blood request from a hospital or patient.
    Stores urgency level, required units, and allocated unit IDs when fulfilled.
    """

    def __init__(
        self,
        request_id: str,
        recipient_id: str,
        recipient_name: str,
        blood_group: BloodGroup,
        units_requested: int,
        hospital_name: str,
        urgency: RequestUrgency = RequestUrgency.ROUTINE,
        component_type: BloodComponent = BloodComponent.WHOLE_BLOOD,
        request_date: Optional[datetime] = None,
        status: RequestStatus = RequestStatus.PENDING,
        allocated_unit_ids: Optional[List[str]] = None,
        notes: str = ""
    ):
        self._request_id = request_id.strip()
        self._recipient_id = recipient_id.strip()
        self._recipient_name = recipient_name.strip()
        self._blood_group = blood_group
        self.units_requested = units_requested  # Property setter validation
        self._hospital_name = hospital_name.strip()
        self._urgency = urgency
        self._component_type = component_type
        self._request_date = request_date or datetime.now()
        self._status = status
        self._allocated_unit_ids: List[str] = allocated_unit_ids or []
        self._notes = notes.strip()

    @property
    def request_id(self) -> str:
        return self._request_id

    @property
    def recipient_id(self) -> str:
        return self._recipient_id

    @property
    def recipient_name(self) -> str:
        return self._recipient_name

    @property
    def blood_group(self) -> BloodGroup:
        return self._blood_group

    @property
    def units_requested(self) -> int:
        return self._units_requested

    @units_requested.setter
    def units_requested(self, val: int):
        if not isinstance(val, int) or val <= 0:
            raise ValueError("Requested units must be a positive integer greater than zero")
        self._units_requested = val

    @property
    def hospital_name(self) -> str:
        return self._hospital_name

    @property
    def urgency(self) -> RequestUrgency:
        return self._urgency

    @urgency.setter
    def urgency(self, val: RequestUrgency):
        self._urgency = val

    @property
    def component_type(self) -> BloodComponent:
        return self._component_type

    @property
    def request_date(self) -> datetime:
        return self._request_date

    @property
    def status(self) -> RequestStatus:
        return self._status

    @property
    def allocated_unit_ids(self) -> List[str]:
        return list(self._allocated_unit_ids)

    @property
    def notes(self) -> str:
        return self._notes

    # --- Lifecycle Methods ---

    def fulfill_with_units(self, unit_ids: List[str]):
        """Attaches allocated blood unit IDs and marks request fulfilled."""
        if len(unit_ids) < self._units_requested:
            raise ValueError(
                f"Insufficient units to fully fulfill request: provided {len(unit_ids)}, required {self._units_requested}"
            )
        self._allocated_unit_ids = unit_ids[:self._units_requested]
        self._status = RequestStatus.FULFILLED

    def reject(self, reason: str = ""):
        self._status = RequestStatus.REJECTED
        if reason:
            self._notes = f"{self._notes} | Rejected: {reason}".strip(" |")

    def cancel(self):
        self._status = RequestStatus.CANCELLED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self._request_id,
            "recipient_id": self._recipient_id,
            "recipient_name": self._recipient_name,
            "blood_group": self._blood_group.value,
            "units_requested": self._units_requested,
            "hospital_name": self._hospital_name,
            "urgency": self._urgency.value,
            "component_type": self._component_type.value,
            "request_date": self._request_date.isoformat(),
            "status": self._status.value,
            "allocated_unit_ids": self._allocated_unit_ids,
            "notes": self._notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BloodRequest":
        # Match urgency
        urgency_match = RequestUrgency.ROUTINE
        for u in RequestUrgency:
            if u.value == data.get("urgency"):
                urgency_match = u
                break

        # Match status
        status_match = RequestStatus.PENDING
        for s in RequestStatus:
            if s.value == data.get("status"):
                status_match = s
                break

        # Match component
        comp_match = BloodComponent.WHOLE_BLOOD
        for c in BloodComponent:
            if c.value == data.get("component_type"):
                comp_match = c
                break

        return cls(
            request_id=data["request_id"],
            recipient_id=data["recipient_id"],
            recipient_name=data.get("recipient_name", "Anonymous Patient"),
            blood_group=BloodGroup.from_string(data["blood_group"]),
            units_requested=int(data["units_requested"]),
            hospital_name=data.get("hospital_name", "General Hospital"),
            urgency=urgency_match,
            component_type=comp_match,
            request_date=datetime.fromisoformat(data["request_date"]),
            status=status_match,
            allocated_unit_ids=data.get("allocated_unit_ids", []),
            notes=data.get("notes", "")
        )


class DonationRecord:
    """
    Immutable historical audit log of a successful blood donation transaction.
    """

    def __init__(
        self,
        record_id: str,
        donor_id: str,
        donor_name: str,
        blood_group: BloodGroup,
        unit_id: str,
        donation_date: date,
        staff_id: str = "STAFF-001",
        camp_or_facility: str = "Central Blood Bank"
    ):
        self._record_id = record_id
        self._donor_id = donor_id
        self._donor_name = donor_name
        self._blood_group = blood_group
        self._unit_id = unit_id
        self._donation_date = donation_date
        self._staff_id = staff_id
        self._camp_or_facility = camp_or_facility

    @property
    def record_id(self) -> str:
        return self._record_id

    @property
    def donor_id(self) -> str:
        return self._donor_id

    @property
    def donor_name(self) -> str:
        return self._donor_name

    @property
    def blood_group(self) -> BloodGroup:
        return self._blood_group

    @property
    def unit_id(self) -> str:
        return self._unit_id

    @property
    def donation_date(self) -> date:
        return self._donation_date

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self._record_id,
            "donor_id": self._donor_id,
            "donor_name": self._donor_name,
            "blood_group": self._blood_group.value,
            "unit_id": self._unit_id,
            "donation_date": self._donation_date.isoformat(),
            "staff_id": self._staff_id,
            "camp_or_facility": self._camp_or_facility
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DonationRecord":
        return cls(
            record_id=data["record_id"],
            donor_id=data["donor_id"],
            donor_name=data.get("donor_name", "Unknown Donor"),
            blood_group=BloodGroup.from_string(data["blood_group"]),
            unit_id=data["unit_id"],
            donation_date=datetime.fromisoformat(data["donation_date"]).date(),
            staff_id=data.get("staff_id", "STAFF-001"),
            camp_or_facility=data.get("camp_or_facility", "Central Blood Bank")
        )
