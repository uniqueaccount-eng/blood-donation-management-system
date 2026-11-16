# System Architecture & UML Diagrams

This document contains visual Object-Oriented representations of the Blood Donation Management System (BDMS) using Mermaid UML specifications.

---

## 1. Class Diagram (Object-Oriented Structure)

```mermaid
classDiagram
    direction TB

    class Person {
        <<abstract>>
        #str _id
        #str _first_name
        #str _last_name
        #BloodGroup _blood_group
        #str _contact_number
        #str _email
        #int _age
        #str _gender
        #str _city
        +id : str
        +full_name : str
        +blood_group : BloodGroup
        +age : int
        +get_role_description()* str
        +to_dict()* dict
    }

    class Donor {
        -float _weight_kg
        -date _last_donation_date
        -int _total_donations
        -str _medical_conditions
        +weight_kg : float
        +evaluate_eligibility() tuple
        +record_new_donation(date)
        +get_role_description() str
        +to_dict() dict
    }

    class Recipient {
        -str _hospital_name
        -str _doctor_in_charge
        +hospital_name : str
        +get_role_description() str
        +to_dict() dict
    }

    class MedicalStaff {
        -str _license_number
        -str _designation
        +get_role_description() str
        +to_dict() dict
    }

    class BloodUnit {
        -str _unit_id
        -BloodGroup _blood_group
        -str _donor_id
        -BloodComponent _component_type
        -float _volume_ml
        -date _collected_date
        -date _expiry_date
        -UnitStatus _status
        -str _storage_location
        +days_until_expiry() int
        +is_expired() bool
        +check_and_update_expiry() bool
        +reserve()
        +transfuse(recipient_id)
        +to_dict() dict
    }

    class BloodRequest {
        -str _request_id
        -str _recipient_id
        -str _recipient_name
        -BloodGroup _blood_group
        -int _units_requested
        -RequestUrgency _urgency
        -RequestStatus _status
        -List~str~ _allocated_unit_ids
        +fulfill_with_units(unit_ids)
        +reject(reason)
        +cancel()
        +to_dict() dict
    }

    class CompatibilityStrategy {
        <<interface>>
        +get_compatible_donors(recipient_group)* Set
        +is_compatible(donor_group, recipient_group)* bool
    }

    class RedBloodCellCompatibilityStrategy {
        +get_compatible_donors(recipient_group) Set
        +is_compatible(donor_group, recipient_group) bool
    }

    class PlasmaCompatibilityStrategy {
        +get_compatible_donors(recipient_group) Set
        +is_compatible(donor_group, recipient_group) bool
    }

    class InventoryManager {
        <<singleton>>
        -List~BloodUnit~ _units
        -List~Callable~ _observers
        +add_unit(BloodUnit)
        +get_available_units() List
        +allocate_units_fifo() List
        +get_stock_counts() dict
        +refresh_expiries() int
        +register_observer(callback)
    }

    class RequestService {
        -StorageProvider _storage
        -InventoryManager _inventory
        -BloodCompatibilityService _compatibility
        +create_request(BloodRequest)
        +match_and_fulfill(request_id) tuple
    }

    Person <|-- Donor : Inheritance
    Person <|-- Recipient : Inheritance
    Person <|-- MedicalStaff : Inheritance

    CompatibilityStrategy <|.. RedBloodCellCompatibilityStrategy : Implements
    CompatibilityStrategy <|.. PlasmaCompatibilityStrategy : Implements

    InventoryManager o-- BloodUnit : Manages
    RequestService --> InventoryManager : Uses
    RequestService --> CompatibilityStrategy : Uses Strategy
    RequestService o-- BloodRequest : Coordinates
    Donor "1" --> "*" BloodUnit : Donates
```

---

## 2. Sequence Diagram (Emergency Blood Requisition & FIFO Matching)

```mermaid
sequenceDiagram
    autonumber
    actor Hospital as Hospital Doctor
    participant UI as RequestView (GUI)
    participant ReqSvc as RequestService
    participant Compat as BloodCompatibilityService
    participant InvMgr as InventoryManager (Singleton)
    participant Storage as JSONStorage

    Hospital->>UI: Submit Emergency Blood Requisition (Patient, BloodGroup, Units)
    UI->>ReqSvc: create_request(BloodRequest)
    ReqSvc->>Storage: save_requests()
    ReqSvc-->>UI: Request Enqueued (Status: PENDING)

    Hospital->>UI: Click "Match & Fulfill"
    UI->>ReqSvc: match_and_fulfill(request_id)
    ReqSvc->>Compat: get_compatible_donor_groups(req.blood_group, req.component)
    Compat-->>ReqSvc: Return compatible groups (e.g. [O-, A-])
    
    ReqSvc->>InvMgr: allocate_units_fifo(allowed_groups, units_needed)
    Note over InvMgr: Filters available units & sorts by earliest expiry date (FIFO)
    InvMgr->>InvMgr: Reserve selected units
    InvMgr-->>ReqSvc: Return allocated BloodUnits
    
    ReqSvc->>InvMgr: mark_units_transfused(unit_ids, recipient_id)
    InvMgr->>Storage: save_inventory()
    ReqSvc->>Storage: save_requests() (Status: FULFILLED)
    
    ReqSvc-->>UI: Success Notification + Dispatched Unit Barcodes
    UI-->>Hospital: Display Confirmation & Dispatch Dialog
```

---

## 3. Use Case Diagram

```mermaid
flowchart LR
    subgraph Actors
        D[Donor]
        S[Medical Staff / Admin]
        H[Hospital / Recipient]
    end

    subgraph BDMS ["Blood Donation Management System"]
        UC1([Register as Donor])
        UC2([Clinical Eligibility Screening])
        UC3([Collect & Barcode Blood Unit])
        UC4([Monitor Cold Storage & Expiries])
        UC5([Create Emergency Requisition])
        UC6([Automated Cross-Match & Allocation])
        UC7([FIFO Biohazard Audit & Disposal])
        UC8([View SDG 3 Analytics & Reports])
    end

    D --> UC1
    UC1 -.->|includes| UC2
    S --> UC3
    S --> UC4
    S --> UC7
    H --> UC5
    S --> UC6
    UC5 -.->|triggers| UC6
    S --> UC8
```
