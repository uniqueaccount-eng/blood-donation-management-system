# Project Synopsis: Blood Donation Management System (BDMS)

**Course:** Object-Oriented Programming (OOP) - 2nd Year  
**Author:** uniqueaccount-eng (maitreyarakesh11@gmail.com)  
**Project Title:** Blood Donation Management System  
**SDG Alignment:** SDG 3 (Good Health and Well-Being), SDG 12, SDG 10  

---

## 1. Problem Addressed and Problem Definition

### Problem Statement
In emergency medical situations like road accidents, emergency surgeries, and maternal childbirth complications, timely access to safe and compatible blood is critical to save lives. However, many blood banks and hospital blood storage centers still rely on manual record-keeping or simple spreadsheets.

This leads to several critical issues:
1. **Delay in Finding Compatible Blood:** In emergency cases, medical staff have to manually verify which donors or units match the patient's blood group. For rare blood groups (such as O-negative or AB-negative), this delay can be dangerous.
2. **Blood Wastage Due to Expiration:** Blood has a limited shelf life (Whole blood lasts 35 days, while platelets last only 5 days). Without an automated inventory system, units that were collected earlier often sit in storage while newer units get used first, causing preventable wastage.
3. **Donor Health Risks:** Donors should wait at least 90 days between donations to allow their hemoglobin and iron levels to recover. Manual systems often fail to check this cooldown interval.
4. **Lack of Stock Awareness:** Blood banks often face unexpected shortages of specific blood groups because there is no automated low-stock alerting.

### Problem Solved by the Project
This project provides a desktop-based software system that:
* Maintains a centralized donor registry with automatic checks for age, weight, and donation cooldown.
* Automates biological ABO/Rh cross-matching so that only compatible blood units are selected.
* Implements a First-In, First-Out (FIFO) algorithm to allocate units closest to expiration first.
* Provides live alerts when any blood group stock falls below a safe minimum threshold.

---

## 2. Approach Used (OOP Architecture)

The system is developed using Python and Tkinter, structured around the four core OOP concepts and design patterns:

### Core OOP Concepts
* **Encapsulation:** Attributes like age, weight, blood group, and unit status are kept protected (`_age`, `_weight_kg`, `_blood_group`). Getters and setters with validation ensure that incorrect data cannot be entered (for example, negative numbers, invalid email formats, or out-of-range donor age).
* **Inheritance:** An abstract base class `Person` contains common attributes (ID, name, contact, age, gender, blood group). Three specialized child classes inherit from it:
  * `Donor`: adds weight, last donation date, total donations, and medical history.
  * `Recipient`: adds hospital name and attending doctor.
  * `MedicalStaff`: adds staff license number and designation.
* **Polymorphism:** Methods such as `get_role_description()` and `to_dict()` are declared in the base class and overridden in each subclass to give role-specific outputs.
* **Abstraction:** The `Person` class and the `StorageProvider` class are abstract base classes (using `abc.ABC`). The business logic interacts with `StorageProvider` without needing to know the low-level details of JSON file handling.

### Design Patterns
* **Strategy Pattern (`CompatibilityStrategy`):** Encapsulates the rules for blood compatibility. Separate strategy classes handle red blood cell matching and plasma matching, allowing clean separation of biological rules.
* **Singleton Pattern (`InventoryManager`):** Ensures that only one inventory manager instance exists throughout the application, keeping stock counts consistent across all screens.
* **Observer Pattern:** The inventory manager notifies the UI whenever stock changes, so the dashboard and alerts update automatically.

---

## 3. SDG Mapping

| Goal | Target | Relevance to this Project |
| :--- | :--- | :--- |
| **SDG 3: Good Health & Well-Being** *(Primary)* | **Target 3.8:** Access to safe, effective, and affordable essential healthcare services. | Blood is an essential medical resource. Automating the supply chain helps hospitals get safe blood faster. |
| **SDG 3: Good Health & Well-Being** *(Primary)* | **Target 3.6 & 3.2:** Halving road accident deaths and ending preventable maternal mortality. | Quick matching reduces the waiting time for emergency transfusions during road trauma and postpartum bleeding. |
| **SDG 12: Responsible Consumption** *(Secondary)* | **Target 12.5:** Substantially reduce waste generation. | FIFO allocation uses older viable blood first, cutting down on expired blood units. |
| **SDG 10: Reduced Inequalities** *(Secondary)* | **Target 10.2:** Equal access without discrimination. | Automated priority queuing (Critical > Urgent > Routine) ensures blood is allocated purely based on medical need. |

---

## 4. Methodology Used

The development followed an iterative software development approach:

1. **Requirements Gathering:** Defined the clinical criteria for blood collection (donor age 18-65, weight >= 50 kg, 90-day donation interval) and built the compatibility matrix for all 8 blood groups (A+, A-, B+, B-, AB+, AB-, O+, O-).
2. **System Design (UML):**
   * Designed class hierarchy diagrams showing inheritance and associations.
   * Created sequence diagrams for the blood requisition and allocation workflow.
   * Outlined use cases for Donors, Medical Staff, and Hospital Requisitions.
3. **Implementation:**
   * Built domain models in `models/`.
   * Implemented matching and inventory services in `services/`.
   * Created a clean Tkinter GUI in `ui/` with tabbed navigation.
4. **Testing:**
   * Wrote automated unit tests in `tests/test_oop_system.py` to test eligibility rules, compatibility tables, and FIFO dispatch.

---

## 5. Expected Outcomes

* Fast and error-free matching between donor units and patient blood requests.
* Significant reduction in expired blood units through FIFO dispatching.
* Clear visibility of current stock levels across all eight blood groups with shortage warnings.
* Safe donor management that prevents over-donation through automated 90-day cooldown tracking.
* A clean, working desktop application ready to run on any computer with Python installed.
