"""
models/person.py
Base Person class and subclasses (Donor, Recipient, MedicalStaff).
Uses inheritance, property getters/setters for encapsulation, and abstract methods.
"""
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from models.enums import BloodGroup, DonorStatus


class Person(ABC):
    """
    Abstract base class for all persons in the system.
    Stores basic details like name, blood group, contact, and age.
    """

    def __init__(
        self,
        person_id: str,
        first_name: str,
        last_name: str,
        blood_group: BloodGroup,
        contact_number: str,
        email: str,
        age: int,
        gender: str,
        city: str = ""
    ):
        self._id = person_id
        self._first_name = first_name.strip()
        self._last_name = last_name.strip()
        self._blood_group = blood_group
        self._contact_number = contact_number.strip()
        self._email = email.strip()
        self.age = age  # Uses setter for validation
        self._gender = gender.strip().capitalize()
        self._city = city.strip()
        self._created_at = datetime.now()

    # --- Encapsulation: Getters and Setters with Validation ---

    @property
    def id(self) -> str:
        return self._id

    @property
    def full_name(self) -> str:
        return f"{self._first_name} {self._last_name}"

    @property
    def blood_group(self) -> BloodGroup:
        return self._blood_group

    @blood_group.setter
    def blood_group(self, value: BloodGroup):
        if not isinstance(value, BloodGroup):
            raise TypeError("blood_group must be an instance of BloodGroup enum")
        self._blood_group = value

    @property
    def contact_number(self) -> str:
        return self._contact_number

    @contact_number.setter
    def contact_number(self, value: str):
        cleaned = value.strip().replace(" ", "").replace("-", "")
        if len(cleaned) < 8 or not cleaned.replace("+", "").isdigit():
            raise ValueError("Contact number must contain at least 8 digits")
        self._contact_number = value.strip()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, value: str):
        if "@" not in value or "." not in value:
            raise ValueError("Invalid email format")
        self._email = value.strip()

    @property
    def age(self) -> int:
        return self._age

    @age.setter
    def age(self, value: int):
        if not isinstance(value, int) or value <= 0 or value > 120:
            raise ValueError("Age must be an integer between 1 and 120")
        self._age = value

    @property
    def gender(self) -> str:
        return self._gender

    @property
    def city(self) -> str:
        return self._city

    @city.setter
    def city(self, value: str):
        self._city = value.strip()

    # --- Abstract Methods (Contract Enforced on Subclasses) ---

    @abstractmethod
    def get_role_description(self) -> str:
        """Returns a string description of the role in the blood management lifecycle."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serializes entity state to a dictionary for persistence."""
        pass


class Donor(Person):
    """
    Subclass of Person representing a blood donor.
    Extends base attributes with clinical qualification fields.
    """

    MIN_DONATION_INTERVAL_DAYS = 90  # WHO standard safe interval: 3 months (90 days)
    MIN_DONOR_WEIGHT_KG = 50.0
    MIN_DONOR_AGE = 18
    MAX_DONOR_AGE = 65

    def __init__(
        self,
        person_id: str,
        first_name: str,
        last_name: str,
        blood_group: BloodGroup,
        contact_number: str,
        email: str,
        age: int,
        gender: str,
        weight_kg: float,
        last_donation_date: Optional[date] = None,
        total_donations: int = 0,
        medical_conditions: str = "None",
        city: str = ""
    ):
        super().__init__(
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            blood_group=blood_group,
            contact_number=contact_number,
            email=email,
            age=age,
            gender=gender,
            city=city
        )
        self.weight_kg = weight_kg  # Uses setter for validation
        self._last_donation_date = last_donation_date
        self._total_donations = max(0, total_donations)
        self._medical_conditions = medical_conditions.strip()

    @property
    def weight_kg(self) -> float:
        return self._weight_kg

    @weight_kg.setter
    def weight_kg(self, value: float):
        if value <= 0:
            raise ValueError("Weight must be greater than 0 kg")
        self._weight_kg = float(value)

    @property
    def last_donation_date(self) -> Optional[date]:
        return self._last_donation_date

    @last_donation_date.setter
    def last_donation_date(self, value: Optional[date]):
        self._last_donation_date = value

    @property
    def total_donations(self) -> int:
        return self._total_donations

    @property
    def medical_conditions(self) -> str:
        return self._medical_conditions

    # --- Business Logic & Polymorphic Implementation ---

    def evaluate_eligibility(self) -> tuple[DonorStatus, str]:
        """
        Evaluates donor eligibility based on international clinical guidelines (WHO / Red Cross).
        Returns: (DonorStatus, explanation_reason)
        """
        # Age check
        if self._age < self.MIN_DONOR_AGE:
            return DonorStatus.PERMANENT_DEFERRAL, f"Underage: Minimum age is {self.MIN_DONOR_AGE} years."
        if self._age > self.MAX_DONOR_AGE:
            return DonorStatus.PERMANENT_DEFERRAL, f"Overage: Maximum age is {self.MAX_DONOR_AGE} years."

        # Weight check
        if self._weight_kg < self.MIN_DONOR_WEIGHT_KG:
            return (
                DonorStatus.TEMPORARY_DEFERRAL,
                f"Underweight: Minimum weight is {self.MIN_DONOR_WEIGHT_KG} kg (current: {self._weight_kg} kg)."
            )

        # High-risk chronic medical conditions
        chronic_keywords = ["hiv", "hepatitis", "cancer", "leukemia", "cardiac arrest"]
        cond_lower = self._medical_conditions.lower()
        for kw in chronic_keywords:
            if kw in cond_lower:
                return DonorStatus.PERMANENT_DEFERRAL, f"Permanent deferral due to medical history: {kw}."

        # Donation cooldown interval check
        if self._last_donation_date:
            days_since = (date.today() - self._last_donation_date).days
            if days_since < self.MIN_DONATION_INTERVAL_DAYS:
                days_left = self.MIN_DONATION_INTERVAL_DAYS - days_since
                return (
                    DonorStatus.TEMPORARY_DEFERRAL,
                    f"Cooldown period active: Eligible in {days_left} day(s) (Last donated {days_since} days ago)."
                )

        return DonorStatus.ELIGIBLE, "Qualified and eligible to donate."

    def record_new_donation(self, donation_date: Optional[date] = None):
        """Records a successful donation and advances counts."""
        self._last_donation_date = donation_date or date.today()
        self._total_donations += 1

    def get_role_description(self) -> str:
        """Polymorphic implementation of Person contract."""
        eligibility, reason = self.evaluate_eligibility()
        return (
            f"Blood Donor [{self.full_name}, {self.blood_group.value}] "
            f"- Status: {eligibility.value} ({reason})"
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": "Donor",
            "first_name": self._first_name,
            "last_name": self._last_name,
            "blood_group": self.blood_group.value,
            "contact_number": self.contact_number,
            "email": self.email,
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
            "weight_kg": self.weight_kg,
            "last_donation_date": self.last_donation_date.isoformat() if self.last_donation_date else None,
            "total_donations": self.total_donations,
            "medical_conditions": self.medical_conditions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Donor":
        last_date = (
            datetime.fromisoformat(data["last_donation_date"]).date()
            if data.get("last_donation_date")
            else None
        )
        return cls(
            person_id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            blood_group=BloodGroup.from_string(data["blood_group"]),
            contact_number=data["contact_number"],
            email=data["email"],
            age=int(data["age"]),
            gender=data["gender"],
            weight_kg=float(data.get("weight_kg", 60.0)),
            last_donation_date=last_date,
            total_donations=int(data.get("total_donations", 0)),
            medical_conditions=data.get("medical_conditions", "None"),
            city=data.get("city", "")
        )


class Recipient(Person):
    """
    Subclass of Person representing a patient/recipient requiring blood transfusion.
    """

    def __init__(
        self,
        person_id: str,
        first_name: str,
        last_name: str,
        blood_group: BloodGroup,
        contact_number: str,
        email: str,
        age: int,
        gender: str,
        hospital_name: str,
        doctor_in_charge: str = "",
        city: str = ""
    ):
        super().__init__(
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            blood_group=blood_group,
            contact_number=contact_number,
            email=email,
            age=age,
            gender=gender,
            city=city
        )
        self._hospital_name = hospital_name.strip()
        self._doctor_in_charge = doctor_in_charge.strip()

    @property
    def hospital_name(self) -> str:
        return self._hospital_name

    @property
    def doctor_in_charge(self) -> str:
        return self._doctor_in_charge

    def get_role_description(self) -> str:
        return f"Recipient Patient [{self.full_name}, {self.blood_group.value}] admitted at {self.hospital_name}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": "Recipient",
            "first_name": self._first_name,
            "last_name": self._last_name,
            "blood_group": self.blood_group.value,
            "contact_number": self.contact_number,
            "email": self.email,
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
            "hospital_name": self.hospital_name,
            "doctor_in_charge": self.doctor_in_charge
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Recipient":
        return cls(
            person_id=data["id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            blood_group=BloodGroup.from_string(data["blood_group"]),
            contact_number=data["contact_number"],
            email=data["email"],
            age=int(data["age"]),
            gender=data["gender"],
            hospital_name=data.get("hospital_name", "General Hospital"),
            doctor_in_charge=data.get("doctor_in_charge", ""),
            city=data.get("city", "")
        )


class MedicalStaff(Person):
    """
    Subclass of Person representing hospital blood bank staff/technicians.
    """

    def __init__(
        self,
        person_id: str,
        first_name: str,
        last_name: str,
        blood_group: BloodGroup,
        contact_number: str,
        email: str,
        age: int,
        gender: str,
        license_number: str,
        designation: str = "Blood Bank Officer",
        city: str = ""
    ):
        super().__init__(
            person_id=person_id,
            first_name=first_name,
            last_name=last_name,
            blood_group=blood_group,
            contact_number=contact_number,
            email=email,
            age=age,
            gender=gender,
            city=city
        )
        self._license_number = license_number
        self._designation = designation

    @property
    def designation(self) -> str:
        return self._designation

    def get_role_description(self) -> str:
        return f"Staff: {self.full_name} ({self.designation}) - License: {self._license_number}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "role": "MedicalStaff",
            "first_name": self._first_name,
            "last_name": self._last_name,
            "blood_group": self.blood_group.value,
            "contact_number": self.contact_number,
            "email": self.email,
            "age": self.age,
            "gender": self.gender,
            "city": self.city,
            "license_number": self._license_number,
            "designation": self._designation
        }
