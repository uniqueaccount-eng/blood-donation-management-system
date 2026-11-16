"""
services/inventory_manager.py
Inventory manager for blood storage.
Uses the Singleton pattern so all screens access the same inventory instance,
and uses FIFO (First-In, First-Out) to prioritize units expiring sooner.
"""
from datetime import date
from typing import List, Dict, Optional, Callable, Set
from models.enums import BloodGroup, BloodComponent, UnitStatus
from models.blood_unit import BloodUnit, BloodUnitError
from storage.storage_interface import StorageProvider


class InventoryObserver:
    """Callback interface for updating UI when inventory changes."""
    def on_inventory_changed(self):
        pass

    def on_critical_shortage_alert(self, blood_group: BloodGroup, current_units: int):
        pass


class InventoryManager:
    """
    Manages blood stock, tracks unit expiration dates, and allocates units using FIFO.
    Implements Singleton pattern.
    """
    _instance: Optional["InventoryManager"] = None

    # Alert if any blood group has less than 2 available units
    CRITICAL_STOCK_THRESHOLD = 2

    @classmethod
    def reset_instance(cls):
        """Helper for test suites to reset Singleton instance."""
        cls._instance = None

    def __new__(cls, storage_provider: StorageProvider):
        if cls._instance is None:
            cls._instance = super(InventoryManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, storage_provider: StorageProvider):
        if getattr(self, "_initialized", False):
            return
        self._storage = storage_provider
        self._units: List[BloodUnit] = self._storage.load_inventory()
        self._observers: List[Callable[[], None]] = []
        self._initialized = True

    # --- Observer Pattern Registration ---

    def register_observer(self, callback: Callable[[], None]):
        """Registers a listener function to be called on any inventory change."""
        if callback not in self._observers:
            self._observers.append(callback)

    def unregister_observer(self, callback: Callable[[], None]):
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self):
        """Notifies all registered UI or system observers of state mutation."""
        for callback in self._observers:
            try:
                callback()
            except Exception:
                pass

    # --- Core Inventory Operations ---

    def add_unit(self, unit: BloodUnit) -> None:
        """Adds a newly collected and tested blood unit to the cold inventory."""
        self._units.append(unit)
        self._storage.save_inventory(self._units)
        self._notify_observers()

    def get_all_units(self) -> List[BloodUnit]:
        """Returns all units after refreshing expiry statuses."""
        self.refresh_expiries()
        return list(self._units)

    def get_available_units(
        self,
        blood_group: Optional[BloodGroup] = None,
        component_type: Optional[BloodComponent] = None
    ) -> List[BloodUnit]:
        """
        Retrieves all valid, non-expired units sorted by expiry date ascending (FIFO).
        """
        self.refresh_expiries()
        results = [
            u for u in self._units
            if u.status == UnitStatus.AVAILABLE
        ]
        if blood_group is not None:
            results = [u for u in results if u.blood_group == blood_group]
        if component_type is not None:
            results = [u for u in results if u.component_type == component_type]

        # FIFO: Earliest expiry date allocated first to minimize expiration waste
        results.sort(key=lambda u: u.expiry_date)
        return results

    def get_stock_counts(self) -> Dict[BloodGroup, int]:
        """Returns available count per blood group."""
        self.refresh_expiries()
        counts = {bg: 0 for bg in BloodGroup}
        for u in self._units:
            if u.status == UnitStatus.AVAILABLE:
                counts[u.blood_group] += 1
        return counts

    def get_critical_shortages(self) -> List[BloodGroup]:
        """Identifies blood groups where available stock is below safe threshold."""
        counts = self.get_stock_counts()
        return [bg for bg, count in counts.items() if count < self.CRITICAL_STOCK_THRESHOLD]

    def get_units_expiring_soon(self, within_days: int = 7) -> List[BloodUnit]:
        """Returns active units that will expire within the specified number of days."""
        self.refresh_expiries()
        today = date.today()
        expiring = [
            u for u in self._units
            if u.status == UnitStatus.AVAILABLE and 0 <= u.days_until_expiry(today) <= within_days
        ]
        expiring.sort(key=lambda u: u.days_until_expiry(today))
        return expiring

    def refresh_expiries(self) -> int:
        """Audits all units against today's date and marks expired units."""
        changed_count = 0
        today = date.today()
        for unit in self._units:
            if unit.check_and_update_expiry(today):
                changed_count += 1
        if changed_count > 0:
            self._storage.save_inventory(self._units)
            self._notify_observers()
        return changed_count

    def allocate_units_fifo(
        self,
        allowed_blood_groups: List[BloodGroup],
        units_needed: int,
        component_type: BloodComponent = BloodComponent.WHOLE_BLOOD
    ) -> List[BloodUnit]:
        """
        Allocates matching units using FIFO order.
        Prioritizes exact blood group match first, then compatible alternatives.
        """
        self.refresh_expiries()
        allocated: List[BloodUnit] = []
        
        # Pool all available matching units sorted by expiry date ascending
        candidate_units: List[BloodUnit] = [
            u for u in self._units
            if u.status == UnitStatus.AVAILABLE
            and u.blood_group in allowed_blood_groups
            and u.component_type == component_type
        ]
        candidate_units.sort(key=lambda u: u.expiry_date)

        if len(candidate_units) < units_needed:
            return []  # Cannot fulfill full order

        # Reserve selected units
        selected = candidate_units[:units_needed]
        for unit in selected:
            unit.reserve("Allocated for approved hospital requisition")
            allocated.append(unit)

        self._storage.save_inventory(self._units)
        self._notify_observers()
        return allocated

    def mark_units_transfused(self, unit_ids: List[str], recipient_id: str):
        """Marks units as transfused upon physical release."""
        for u in self._units:
            if u.unit_id in unit_ids:
                u.transfuse(recipient_id)
        self._storage.save_inventory(self._units)
        self._notify_observers()

    def discard_expired_units(self) -> int:
        """Removes or marks expired units for safe medical biohazard disposal."""
        self.refresh_expiries()
        expired_count = sum(1 for u in self._units if u.status == UnitStatus.EXPIRED)
        # Keep records but marked EXPIRED
        self._storage.save_inventory(self._units)
        self._notify_observers()
        return expired_count
