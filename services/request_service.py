"""
services/request_service.py
Service for creating hospital blood requests and matching them with compatible blood units.
"""
from datetime import datetime
from typing import List, Optional, Tuple
from models.enums import BloodGroup, BloodComponent, RequestUrgency, RequestStatus
from models.request import BloodRequest
from models.blood_unit import BloodUnit
from services.compatibility import BloodCompatibilityService
from services.inventory_manager import InventoryManager
from storage.storage_interface import StorageProvider


class RequestService:
    """
    Handles blood requests, prioritizes urgent cases, and fulfills requests using compatible units.
    """

    def __init__(
        self,
        storage_provider: StorageProvider,
        inventory_manager: InventoryManager,
        compatibility_service: BloodCompatibilityService
    ):
        self._storage = storage_provider
        self._inventory = inventory_manager
        self._compatibility = compatibility_service
        self._requests: List[BloodRequest] = self._storage.load_requests()

    def create_request(self, request: BloodRequest) -> BloodRequest:
        """Enqueues a new blood requisition."""
        if any(r.request_id == request.request_id for r in self._requests):
            raise ValueError(f"Request ID '{request.request_id}' already exists.")
        self._requests.append(request)
        self._storage.save_requests(self._requests)
        return request

    def get_all_requests(self) -> List[BloodRequest]:
        """Returns requests sorted with critical emergencies first."""
        priority_order = {
            RequestUrgency.CRITICAL: 0,
            RequestUrgency.URGENT: 1,
            RequestUrgency.ROUTINE: 2
        }
        return sorted(self._requests, key=lambda r: (priority_order.get(r.urgency, 3), -r.request_date.timestamp()))

    def get_pending_requests(self) -> List[BloodRequest]:
        return [r for r in self.get_all_requests() if r.status == RequestStatus.PENDING]

    def get_request_by_id(self, req_id: str) -> Optional[BloodRequest]:
        for r in self._requests:
            if r.request_id.strip().upper() == req_id.strip().upper():
                return r
        return None

    def match_and_fulfill(self, request_id: str) -> Tuple[bool, str, List[str]]:
        """
        Attempts to fulfill a pending request by finding compatible available units.
        Returns: (success: bool, message: str, allocated_unit_ids: List[str])
        """
        req = self.get_request_by_id(request_id)
        if not req:
            return False, f"Request '{request_id}' not found.", []

        if req.status != RequestStatus.PENDING:
            return False, f"Request is already '{req.status.value}'.", []

        # 1. Determine all compatible donor blood groups
        compatible_groups = self._compatibility.get_compatible_donor_groups(
            recipient_group=req.blood_group,
            component=req.component_type
        )

        # 2. Query FIFO allocation from InventoryManager
        allocated_units = self._inventory.allocate_units_fifo(
            allowed_blood_groups=compatible_groups,
            units_needed=req.units_requested,
            component_type=req.component_type
        )

        if not allocated_units or len(allocated_units) < req.units_requested:
            return False, (
                f"Insufficient inventory to fulfill {req.units_requested} unit(s) "
                f"for blood group {req.blood_group.value}. Compatible groups searched: "
                f"{[bg.value for bg in compatible_groups]}."
            ), []

        # 3. Mark units transfused and fulfill request
        unit_ids = [u.unit_id for u in allocated_units]
        self._inventory.mark_units_transfused(unit_ids, req.recipient_id)
        req.fulfill_with_units(unit_ids)
        self._storage.save_requests(self._requests)

        return True, (
            f"Successfully allocated and dispatched {len(unit_ids)} unit(s) "
            f"({', '.join(unit_ids)}) to {req.hospital_name} for patient {req.recipient_name}."
        ), unit_ids

    def cancel_request(self, request_id: str, reason: str = ""):
        req = self.get_request_by_id(request_id)
        if req and req.status == RequestStatus.PENDING:
            req.cancel()
            self._storage.save_requests(self._requests)
