# Detailed Sustainable Development Goals (SDG) Alignment Report

## Executive Summary
The **HemaCare Blood Donation Management System (BDMS)** was designed not only as an exercise in Object-Oriented Software Engineering, but as an applied solution directly advancing the **United Nations 2030 Agenda for Sustainable Development**.

---

## 1. Primary Alignment: SDG 3 — Good Health and Well-Being

> **Goal 3:** Ensure healthy lives and promote well-being for all at all ages.

### Specific Targets Addressed:
* **Target 3.8: Achieve universal health coverage, including access to safe, effective, quality, and affordable essential medicines and vaccines.**
  * *Application:* Blood and blood products are classified by the World Health Organization (WHO) as **essential medicines**. Millions of patients require blood for chronic conditions (e.g., Thalassemia, Sickle Cell Disease) and acute trauma.
  * *BDMS Contribution:* The platform guarantees systematic recording of blood types, screening statuses, and inventory tracking, ensuring hospitals have reliable, verified access to safe blood units on demand.

* **Target 3.6: By 2030, halve the number of global deaths and injuries from road traffic accidents.**
  * *Application:* Road accidents are the number one consumer of emergency blood reserves globally. Traumatic hemorrhaging leads to death within 30 to 60 minutes if massive transfusion protocol is delayed.
  * *BDMS Contribution:* The automated biological compatibility engine reduces the time required to match compatible donor units from hours to sub-second lookup, directly shortening the "golden hour" transfusion response window.

* **Target 3.1 & 3.2: Reduce maternal mortality and end preventable deaths of newborns and children under 5.**
  * *Application:* Postpartum Hemorrhage (PPH) is the leading cause of maternal mortality in developing nations, accounting for nearly 27% of all maternal deaths.
  * *BDMS Contribution:* Priority requisition tagging (`CRITICAL`) flags obstetric emergencies at the top of hospital dispatch queues, prioritizing instant release of $O^-$ universal or type-specific blood.

---

## 2. Secondary Alignment: SDG 12 — Responsible Consumption and Production

> **Goal 12:** Ensure sustainable consumption and production patterns.

### Specific Target Addressed:
* **Target 12.5: Substantially reduce waste generation through prevention, reduction, recycling and reuse.**
  * *Application:* Blood has a strict biological expiration limit (35–42 days for red cells, 5 days for platelets). Annually, thousands of units are discarded globally due to poor inventory rotation.
  * *BDMS Contribution:* BDMS enforces a **First-In, First-Out (FIFO)** algorithm in `InventoryManager`. When a request is fulfilled, the system automatically selects the unit with the nearest expiration date, drastically minimizing expired biohazard waste.

---

## 3. Secondary Alignment: SDG 10 — Reduced Inequalities

> **Goal 10:** Reduce inequality within and among countries.

### Specific Target Addressed:
* **Target 10.2 & 10.3: Empower and promote social and economic inclusion of all, irrespective of age, sex, disability, race, ethnicity, origin, religion or economic status.**
  * *Application:* In manual or unregulated blood banking systems, rare blood units are often subject to black-market hoarding, personal connections, or economic favoritism.
  * *BDMS Contribution:* Allocation is driven strictly by objective clinical urgency (`CRITICAL` trauma > `URGENT` oncology > `ROUTINE` elective surgery) and biological compatibility, ensuring transparent, egalitarian distribution.

---

## 4. Quantitative Impact Metrics Tracked by the System

1. **Turnaround Latency (Minutes):** Time elapsed between emergency requisition submission and compatible unit allocation (targeted reduction: $> 80\%$).
2. **Biological Wastage Ratio (%):** Percentage of total units expired versus transfused (targeted reduction to $< 2\%$).
3. **Donor Retention Rate (%):** Tracking voluntary recurring donors through safe 90-day cooldown scheduling.
4. **Stockout Frequency:** Number of zero-stock incidents across rare phenotypes ($O^-, B^-, AB^-$).
