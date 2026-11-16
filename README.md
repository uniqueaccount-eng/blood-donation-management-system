# Blood Donation Management System (BDMS)

**Course:** Object Oriented Programming (OOP) - 2nd Year Project  
**Author:** uniqueaccount-eng  
**Email:** maitreyarakesh11@gmail.com  
**Language:** Python 3 (Tkinter GUI)  

---

## Project Overview

The Blood Donation Management System is a desktop application developed to manage blood donors, inventory stock, and emergency blood requests from hospitals. It is designed using Object-Oriented Programming (OOP) concepts in Python with a graphical user interface built using Tkinter.

The project is mapped to **United Nations Sustainable Development Goal 3 (SDG 3: Good Health and Well-Being)**, aiming to reduce delays during medical emergencies and prevent blood wastage in blood banks.

---

## Problem Addressed

During medical emergencies such as road accidents, major surgeries, and maternal complications, finding compatible blood quickly is critical. In many local blood banks and hospitals, records are still maintained manually in registers or simple spreadsheets. This creates several problems:

1. **Slow Matching:** Finding which donor or available blood unit is compatible with a patient takes time, especially for rare groups like O- or AB-.
2. **Blood Expiry and Wastage:** Blood units expire (whole blood lasts about 35 days, while platelets last only 5 days). Without proper tracking, older units sit on shelves and go to waste.
3. **Donor Health and Safety:** Donors must wait at least 90 days between whole blood donations to prevent anemia. Manual records often fail to track this cooldown period.
4. **Lack of Inventory Tracking:** Blood banks often run low on specific blood types without warning.

### What This Project Solves

This software automates the entire workflow:
* Checks donor eligibility (age, weight, and 90-day cooldown period).
* Automatically checks ABO and Rh compatibility between donor and recipient.
* Uses **First-In, First-Out (FIFO)** logic so that blood units expiring sooner are used first.
* Alerts staff when stock for any blood group falls below safe minimum levels.
* Manages emergency requests from hospitals and tracks status from pending to fulfilled.

---

## Sustainable Development Goals (SDG) Mapping

* **Primary: SDG 3 (Good Health and Well-Being)**
  * **Target 3.8:** Ensuring safe, reliable access to essential blood products for patients when needed.
  * **Target 3.6 & 3.2:** Reducing preventable deaths from road traffic accidents and maternal childbirth emergencies by speeding up blood dispatch times.
* **Secondary: SDG 12 (Responsible Consumption and Production)**
  * **Target 12.5:** Reducing biological waste by tracking expiration dates and using the FIFO method.
* **Secondary: SDG 10 (Reduced Inequalities)**
  * Fair, priority-based allocation (Critical > Urgent > Routine) ensuring emergency patients get blood first based on medical need.

---

## OOP Concepts Used in the Project

The project is structured around key Object-Oriented Programming principles:

1. **Encapsulation:**
   * Attributes like age, weight, blood group, and unit status are protected (`_age`, `_weight_kg`).
   * Python property getters and setters validate data before saving (e.g., checking if donor age is between 18 and 65, and weight is at least 50 kg).

2. **Inheritance:**
   * A base class `Person` contains common fields (ID, name, contact, age, gender, blood group).
   * Derived classes `Donor`, `Recipient`, and `MedicalStaff` inherit from `Person` and add their own specific fields.

3. **Polymorphism & Abstraction:**
   * `Person` is an abstract base class using Python's `abc` module.
   * Methods like `get_role_description()` and `to_dict()` are implemented differently in each child class.
   * `StorageProvider` is an abstract interface that defines storage methods, implemented by `JSONStorage`.

4. **Design Patterns:**
   * **Strategy Pattern:** Used for blood compatibility (`RedBloodCellCompatibilityStrategy` and `PlasmaCompatibilityStrategy`) to determine which blood groups can donate to which recipients.
   * **Singleton Pattern:** `InventoryManager` ensures there is only one shared instance managing the blood inventory across all screens.
   * **Observer Pattern:** When blood stock changes, observer functions notify the dashboard to update counters and alert labels.

---

## Project Structure

```text
blood-donation-management-system/
│
├── main.py                     # Entry point to run the application
├── README.md                   # Project documentation
├── requirements.txt            # Dependencies list (uses standard library)
├── .gitignore                  # Git ignore file
│
├── models/                     # OOP Classes
│   ├── __init__.py
│   ├── enums.py                # Blood groups, urgency, and status enums
│   ├── person.py               # Person (base class), Donor, Recipient, Staff
│   ├── blood_unit.py           # BloodUnit class with expiry calculation
│   └── request.py              # BloodRequest and DonationRecord classes
│
├── services/                   # Business logic and algorithms
│   ├── __init__.py
│   ├── compatibility.py        # ABO/Rh compatibility rules (Strategy pattern)
│   ├── inventory_manager.py    # Inventory tracking & FIFO dispatch (Singleton)
│   ├── donor_service.py        # Donor registration and eligibility logic
│   └── request_service.py      # Request handling and matching logic
│
├── storage/                    # Data storage
│   ├── __init__.py
│   ├── storage_interface.py    # Abstract storage interface
│   └── json_storage.py         # JSON file storage with default sample data
│
├── ui/                         # Tkinter GUI
│   ├── __init__.py
│   ├── theme.py                # Colors, fonts, and ttk styles
│   ├── app.py                  # Main GUI window with tab navigation
│   ├── dashboard_view.py       # Dashboard tab (summary cards, stock bars)
│   ├── donor_view.py           # Donors tab (donor list, search, registration)
│   ├── inventory_view.py       # Inventory tab (stock table, expiry warnings)
│   ├── request_view.py         # Requests tab (hospital requests, matching)
│   └── analytics_view.py       # SDG 3 & project info tab
│
├── tests/                      # Unit testing
│   ├── __init__.py
│   └── test_oop_system.py      # Unit tests for OOP classes and logic
│
├── docs/                       # Project documentation
│   ├── project_synopsis.md     # Project synopsis report
│   ├── sdg_mapping.md          # SDG mapping writeup
│   └── uml_diagrams.md         # Class and sequence diagrams
│
└── data/                       # JSON files where data is saved
    ├── donors.json
    ├── inventory.json
    ├── requests.json
    └── donations.json
```

---

## How to Run the Project

### Requirements
* Python 3.8 or higher.
* No extra `pip install` required — the project runs entirely on Python's built-in libraries (`tkinter`, `json`, `datetime`, `unittest`).

### Running the App
1. Open terminal or Command Prompt in the project folder:
   ```bash
   cd blood-donation-management-system
   ```
2. Run the main file:
   ```bash
   python main.py
   ```

### Running Unit Tests
To verify all classes and logic:
```bash
python -m unittest tests/test_oop_system.py
```

---

## Features

* **Dashboard:** Shows total units in stock, registered donors, pending requests, and blood units expiring within 7 days.
* **Donor Management:** Add new donors with instant eligibility check (age 18-65, weight >= 50kg, and 90-day cooldown). Search and filter by name or blood group.
* **Inventory Tracking:** View all blood units with color-coded expiry warnings. Discard expired units.
* **Emergency Requisitions:** Hospitals can request blood by urgency level (Routine, Urgent, Critical). Click "Match & Fulfill" to automatically find compatible units.
* **FIFO Blood Allocation:** Units with the closest expiry date are allocated first to prevent wastage.
* **Data Persistence:** Automatically saves all donors, units, and requests into clean JSON files in the `data/` folder.
