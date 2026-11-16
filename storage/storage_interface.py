"""
storage/storage_interface.py
Demonstrates OOP Abstraction and Interface Segregation.
Defines the storage contract decoupled from specific persistence media.
"""
from abc import ABC, abstractmethod
from typing import List
from models.person import Donor, Recipient
from models.blood_unit import BloodUnit
from models.request import BloodRequest, DonationRecord


class StorageProvider(ABC):
    """
    Abstract interface for persisting and retrieving system state.
    Enables swapping JSON file storage with SQLite, PostgreSQL, or Cloud Storage seamlessly.
    """

    @abstractmethod
    def load_donors(self) -> List[Donor]:
        pass

    @abstractmethod
    def save_donors(self, donors: List[Donor]) -> None:
        pass

    @abstractmethod
    def load_inventory(self) -> List[BloodUnit]:
        pass

    @abstractmethod
    def save_inventory(self, units: List[BloodUnit]) -> None:
        pass

    @abstractmethod
    def load_requests(self) -> List[BloodRequest]:
        pass

    @abstractmethod
    def save_requests(self, requests: List[BloodRequest]) -> None:
        pass

    @abstractmethod
    def load_donations(self) -> List[DonationRecord]:
        pass

    @abstractmethod
    def save_donations(self, donations: List[DonationRecord]) -> None:
        pass
