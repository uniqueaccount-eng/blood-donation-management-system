"""
services/compatibility.py
Blood compatibility rules based on ABO and Rh factors.
Uses the Strategy pattern to separate red blood cell and plasma compatibility.
"""
from abc import ABC, abstractmethod
from typing import List, Set
from models.enums import BloodGroup, BloodComponent


class CompatibilityStrategy(ABC):
    """
    Abstract base class for blood compatibility checks.
    """

    @abstractmethod
    def get_compatible_donors(self, recipient_group: BloodGroup) -> Set[BloodGroup]:
        """Returns the set of blood groups that can donate to this recipient."""
        pass

    @abstractmethod
    def is_compatible(self, donor_group: BloodGroup, recipient_group: BloodGroup) -> bool:
        """Evaluates whether donor blood is biologically safe for recipient."""
        pass


class RedBloodCellCompatibilityStrategy(CompatibilityStrategy):
    """
    Standard RBC / Whole Blood compatibility matrix based on Red Cell antigens.
    Rules:
    - O- is the universal donor.
    - AB+ is the universal recipient.
    - Rh- can donate to Rh+ and Rh-, but Rh+ can only donate to Rh+.
    """

    # Mapping: Recipient Blood Group -> Allowed Donor Blood Groups
    _COMPATIBILITY_MAP = {
        BloodGroup.O_NEG: {BloodGroup.O_NEG},
        BloodGroup.O_POS: {BloodGroup.O_NEG, BloodGroup.O_POS},
        BloodGroup.A_NEG: {BloodGroup.O_NEG, BloodGroup.A_NEG},
        BloodGroup.A_POS: {BloodGroup.O_NEG, BloodGroup.O_POS, BloodGroup.A_NEG, BloodGroup.A_POS},
        BloodGroup.B_NEG: {BloodGroup.O_NEG, BloodGroup.B_NEG},
        BloodGroup.B_POS: {BloodGroup.O_NEG, BloodGroup.O_POS, BloodGroup.B_NEG, BloodGroup.B_POS},
        BloodGroup.AB_NEG: {BloodGroup.O_NEG, BloodGroup.A_NEG, BloodGroup.B_NEG, BloodGroup.AB_NEG},
        BloodGroup.AB_POS: {
            BloodGroup.O_NEG, BloodGroup.O_POS,
            BloodGroup.A_NEG, BloodGroup.A_POS,
            BloodGroup.B_NEG, BloodGroup.B_POS,
            BloodGroup.AB_NEG, BloodGroup.AB_POS
        }
    }

    def get_compatible_donors(self, recipient_group: BloodGroup) -> Set[BloodGroup]:
        return self._COMPATIBILITY_MAP.get(recipient_group, set())

    def is_compatible(self, donor_group: BloodGroup, recipient_group: BloodGroup) -> bool:
        return donor_group in self.get_compatible_donors(recipient_group)


class PlasmaCompatibilityStrategy(CompatibilityStrategy):
    """
    Plasma compatibility matrix based on circulating antibodies.
    In plasma transfusion:
    - AB is universal donor (has no anti-A or anti-B antibodies).
    - O is universal recipient (can receive plasma from any group).
    """

    _PLASMA_COMPATIBILITY_MAP = {
        BloodGroup.O_NEG: {BloodGroup.O_NEG, BloodGroup.O_POS, BloodGroup.A_NEG, BloodGroup.A_POS, BloodGroup.B_NEG, BloodGroup.B_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS},
        BloodGroup.O_POS: {BloodGroup.O_NEG, BloodGroup.O_POS, BloodGroup.A_NEG, BloodGroup.A_POS, BloodGroup.B_NEG, BloodGroup.B_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS},
        BloodGroup.A_NEG: {BloodGroup.A_NEG, BloodGroup.A_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS},
        BloodGroup.A_POS: {BloodGroup.A_NEG, BloodGroup.A_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS},
        BloodGroup.B_NEG: {BloodGroup.B_NEG, BloodGroup.B_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS},
        BloodGroup.B_POS: {BloodGroup.B_NEG, BloodGroup.B_POS, BloodGroup.AB_NEG, BloodGroup.AB_POS},
        BloodGroup.AB_NEG: {BloodGroup.AB_NEG, BloodGroup.AB_POS},
        BloodGroup.AB_POS: {BloodGroup.AB_NEG, BloodGroup.AB_POS}
    }

    def get_compatible_donors(self, recipient_group: BloodGroup) -> Set[BloodGroup]:
        return self._PLASMA_COMPATIBILITY_MAP.get(recipient_group, set())

    def is_compatible(self, donor_group: BloodGroup, recipient_group: BloodGroup) -> bool:
        return donor_group in self.get_compatible_donors(recipient_group)


class BloodCompatibilityService:
    """
    Context class for Strategy Pattern.
    Delegates compatibility checks dynamically based on blood component type.
    """

    def __init__(self):
        self._rbc_strategy = RedBloodCellCompatibilityStrategy()
        self._plasma_strategy = PlasmaCompatibilityStrategy()

    def get_strategy(self, component: BloodComponent) -> CompatibilityStrategy:
        if component == BloodComponent.PLASMA:
            return self._plasma_strategy
        return self._rbc_strategy

    def get_compatible_donor_groups(
        self,
        recipient_group: BloodGroup,
        component: BloodComponent = BloodComponent.WHOLE_BLOOD
    ) -> List[BloodGroup]:
        strategy = self.get_strategy(component)
        compatible = strategy.get_compatible_donors(recipient_group)
        # Sort for stable, predictable ordering
        return sorted(list(compatible), key=lambda bg: bg.value)

    def check_compatibility(
        self,
        donor_group: BloodGroup,
        recipient_group: BloodGroup,
        component: BloodComponent = BloodComponent.WHOLE_BLOOD
    ) -> bool:
        strategy = self.get_strategy(component)
        return strategy.is_compatible(donor_group, recipient_group)

    @staticmethod
    def is_universal_donor(blood_group: BloodGroup) -> bool:
        return blood_group == BloodGroup.O_NEG

    @staticmethod
    def is_universal_recipient(blood_group: BloodGroup) -> bool:
        return blood_group == BloodGroup.AB_POS
