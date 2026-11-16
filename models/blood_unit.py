"""
models/blood_unit.py
Represents a unit of donated blood.
Tracks blood type, volume, collection date, shelf life, and storage status.
"""
from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional
from models.enums import BloodGroup, BloodComponent, UnitStatus


class BloodUnitError(Exception):
    """Custom exception raised for invalid blood unit operations."""
    pass


class BloodUnit:
    """
    Represents an individual unit of blood in storage.
    Calculates expiration date automatically based on component type.
    """

    # Component shelf life in days according to standard hematology guidelines
    SHELF_LIFE_DAYS = {
        BloodComponent.WHOLE_BLOOD: 35,
        BloodComponent.RED_BLOOD_CELLS: 42,
        BloodComponent.PLATELETS: 5,
        BloodComponent.PLASMA: 365
    }

    def __init__(
        self,
        unit_id: str,
        blood_group: BloodGroup,
        donor_id: str,
        component_type: BloodComponent = BloodComponent.WHOLE_BLOOD,
        volume_ml: float = 450.0,
        collected_date: Optional[date] = None,
        expiry_date: Optional[date] = None,
        status: UnitStatus = UnitStatus.AVAILABLE,
        storage_location: str = "Cold Vault A1"
    ):
        self._unit_id = unit_id.strip()
        self._blood_group = blood_group
        self._donor_id = donor_id.strip()
        self._component_type = component_type
        self._volume_ml = float(volume_ml)
        self._collected_date = collected_date or date.today()
        
        # Automatically compute shelf life based on medical standard if not provided
        if expiry_date is None:
            lifespan = self.SHELF_LIFE_DAYS.get(self._component_type, 35)
            self._expiry_date = self._collected_date + timedelta(days=lifespan)
        else:
            self._expiry_date = expiry_date

        self._status = status
        self._storage_location = storage_location.strip()
        
        # Auto-check expiry on initialization
        self.check_and_update_expiry()

    @property
    def unit_id(self) -> str:
        return self._unit_id

    @property
    def blood_group(self) -> BloodGroup:
        return self._blood_group

    @property
    def donor_id(self) -> str:
        return self._donor_id

    @property
    def component_type(self) -> BloodComponent:
        return self._component_type

    @property
    def volume_ml(self) -> float:
        return self._volume_ml

    @property
    def collected_date(self) -> date:
        return self._collected_date

    @property
    def expiry_date(self) -> date:
        return self._expiry_date

    @property
    def status(self) -> UnitStatus:
        return self._status

    @property
    def storage_location(self) -> str:
        return self._storage_location

    @storage_location.setter
    def storage_location(self, loc: str):
        self._storage_location = loc.strip()

    # --- Domain Logic ---

    def days_until_expiry(self, current_date: Optional[date] = None) -> int:
        """Returns the number of days remaining until expiration."""
        ref_date = current_date or date.today()
        return (self._expiry_date - ref_date).days

    def is_expired(self, current_date: Optional[date] = None) -> bool:
        """Checks if the unit has passed its medical safety expiry date."""
        return self.days_until_expiry(current_date) < 0

    def check_and_update_expiry(self, current_date: Optional[date] = None) -> bool:
        """
        Updates unit status to EXPIRED if past shelf-life and currently Available or Reserved.
        Returns True if status was changed.
        """
        if self.is_expired(current_date) and self._status in (UnitStatus.AVAILABLE, UnitStatus.RESERVED):
            self._status = UnitStatus.EXPIRED
            return True
        return False

    def reserve(self, reason: str = ""):
        """Reserves this unit for a confirmed match."""
        self.check_and_update_expiry()
        if self._status != UnitStatus.AVAILABLE:
            raise BloodUnitError(f"Cannot reserve unit {self._unit_id}. Current status: {self._status.value}")
        self._status = UnitStatus.RESERVED

    def release_reservation(self):
        """Releases reservation back to available inventory."""
        if self._status == UnitStatus.RESERVED:
            self._status = UnitStatus.AVAILABLE
            self.check_and_update_expiry()

    def transfuse(self, recipient_id: str):
        """Dispatches unit for transfusion to patient."""
        self.check_and_update_expiry()
        if self._status not in (UnitStatus.AVAILABLE, UnitStatus.RESERVED):
            raise BloodUnitError(
                f"Cannot transfuse unit {self._unit_id} with status '{self._status.value}'. Must be Available or Reserved."
            )
        self._status = UnitStatus.TRANSFUSED

    def quarantine(self, reason: str):
        """Quarantines unit in case of screening flag or cold-chain break."""
        self._status = UnitStatus.QUARANTINED

    def to_dict(self) -> Dict[str, Any]:
        return {
            "unit_id": self._unit_id,
            "blood_group": self._blood_group.value,
            "donor_id": self._donor_id,
            "component_type": self._component_type.value,
            "volume_ml": self._volume_ml,
            "collected_date": self._collected_date.isoformat(),
            "expiry_date": self._expiry_date.isoformat(),
            "status": self._status.value,
            "storage_location": self._storage_location
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BloodUnit":
        coll_date = datetime.fromisoformat(data["collected_date"]).date()
        exp_date = datetime.fromisoformat(data["expiry_date"]).date()
        
        # Match component
        comp_match = BloodComponent.WHOLE_BLOOD
        for c in BloodComponent:
            if c.value == data.get("component_type"):
                comp_match = c
                break

        # Match status
        status_match = UnitStatus.AVAILABLE
        for s in UnitStatus:
            if s.value == data.get("status"):
                status_match = s
                break

        return cls(
            unit_id=data["unit_id"],
            blood_group=BloodGroup.from_string(data["blood_group"]),
            donor_id=data["donor_id"],
            component_type=comp_match,
            volume_ml=float(data.get("volume_ml", 450.0)),
            collected_date=coll_date,
            expiry_date=exp_date,
            status=status_match,
            storage_location=data.get("storage_location", "Cold Vault A1")
        )
