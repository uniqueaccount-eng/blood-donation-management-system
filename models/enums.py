"""
models/enums.py
Defines domain enumeration types for the Blood Donation Management System.
Demonstrates strong type-safety and object modeling.
"""
from enum import Enum

class BloodGroup(str, Enum):
    """
    Standard ABO and Rh D blood group classification.
    """
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"

    @classmethod
    def from_string(cls, value: str) -> "BloodGroup":
        clean_val = value.strip().upper()
        for item in cls:
            if item.value == clean_val:
                return item
        raise ValueError(f"Invalid blood group string: {value}")


class BloodComponent(str, Enum):
    """Types of blood products collected and stored."""
    WHOLE_BLOOD = "Whole Blood"
    RED_BLOOD_CELLS = "Packed Red Blood Cells (PRBC)"
    PLATELETS = "Platelets"
    PLASMA = "Fresh Frozen Plasma (FFP)"


class UnitStatus(str, Enum):
    """Current inventory status of a blood unit."""
    AVAILABLE = "Available"
    RESERVED = "Reserved"
    TRANSFUSED = "Transfused"
    EXPIRED = "Expired"
    QUARANTINED = "Quarantined"


class RequestUrgency(str, Enum):
    """Urgency level of hospital blood requisition."""
    ROUTINE = "Routine"
    URGENT = "Urgent"
    CRITICAL = "Critical (Immediate Life-Saving)"


class RequestStatus(str, Enum):
    """Lifecycle status of a blood request."""
    PENDING = "Pending"
    APPROVED = "Approved"
    FULFILLED = "Fulfilled"
    REJECTED = "Rejected"
    CANCELLED = "Cancelled"


class DonorStatus(str, Enum):
    """Eligibility status of registered blood donors."""
    ELIGIBLE = "Eligible"
    TEMPORARY_DEFERRAL = "Temporary Deferral"
    PERMANENT_DEFERRAL = "Permanent Deferral"
