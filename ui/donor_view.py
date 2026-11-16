"""
ui/donor_view.py
Donor management interface supporting clinical eligibility screening,
search/filtering, registration, and direct donation capture.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from typing import Optional
from models.enums import BloodGroup, DonorStatus, BloodComponent
from models.person import Donor
from models.blood_unit import BloodUnit
from services.donor_service import DonorService
from services.inventory_manager import InventoryManager
import ui.theme as theme


class DonorView(tk.Frame):
    """
    Manages voluntary donors, qualification checks, and intake.
    """

    def __init__(
        self,
        parent: tk.Widget,
        donor_service: DonorService,
        inventory_manager: InventoryManager
    ):
        super().__init__(parent, bg=theme.BG_MAIN)
        self._donors = donor_service
        self._inventory = inventory_manager

        self._build_header()
        self._build_filters()
        self._build_table()
        self._build_action_bar()

    def _build_header(self):
        header = tk.Frame(self, bg=theme.BG_MAIN)
        header.pack(fill="x", padx=20, pady=(15, 5))

        title = tk.Label(
            header,
            text="Donor Management & Eligibility Registry",
            font=theme.FONT_TITLE,
            bg=theme.BG_MAIN,
            fg=theme.TEXT_PRIMARY
        )
        title.pack(side="left")

        desc = tk.Label(
            header,
            text="WHO Clinical Eligibility: Age 18–65, Weight ≥ 50kg, 90-day cooldown interval",
            font=theme.FONT_SMALL,
            bg=theme.BG_MAIN,
            fg=theme.TEXT_SECONDARY
        )
        desc.pack(side="right", pady=(5, 0))

    def _build_filters(self):
        filter_bar = tk.Frame(self, bg=theme.BG_CARD, bd=1, relief="solid", padx=12, pady=10)
        filter_bar.pack(fill="x", padx=20, pady=8)

        # Search Query
        tk.Label(filter_bar, text="Search:", font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD).pack(side="left", padx=(0, 5))
        self.entry_search = ttk.Entry(filter_bar, width=20)
        self.entry_search.pack(side="left", padx=(0, 15))
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_data())

        # Blood Group Filter
        tk.Label(filter_bar, text="Blood Group:", font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD).pack(side="left", padx=(0, 5))
        self.cb_blood_filter = ttk.Combobox(
            filter_bar,
            values=["All"] + [bg.value for bg in BloodGroup],
            state="readonly",
            width=8
        )
        self.cb_blood_filter.current(0)
        self.cb_blood_filter.pack(side="left", padx=(0, 15))
        self.cb_blood_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        # Eligible Only Checkbox
        self.var_only_eligible = tk.BooleanVar(value=False)
        chk = ttk.Checkbutton(
            filter_bar,
            text="Show Only Eligible Donors",
            variable=self.var_only_eligible,
            command=self.refresh_data
        )
        chk.pack(side="left", padx=(0, 10))

        # Reset Button
        btn_reset = ttk.Button(filter_bar, text="Reset Filters", style="Secondary.TButton", command=self._reset_filters)
        btn_reset.pack(side="right")

    def _reset_filters(self):
        self.entry_search.delete(0, "end")
        self.cb_blood_filter.current(0)
        self.var_only_eligible.set(False)
        self.refresh_data()

    def _build_table(self):
        table_frame = tk.Frame(self, bg=theme.BG_CARD, bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        columns = (
            "ID", "Full Name", "Group", "Age", "Gender",
            "Weight", "Contact", "City", "Donations", "Status", "Clinical Reason"
        )
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        col_widths = {
            "ID": 75, "Full Name": 120, "Group": 60, "Age": 45, "Gender": 60,
            "Weight": 65, "Contact": 105, "City": 85, "Donations": 70, "Status": 90, "Clinical Reason": 200
        }
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=col_widths.get(col, 80), anchor="center")
        self.tree.column("Full Name", anchor="w")
        self.tree.column("Clinical Reason", anchor="w")

        # Scrollbars
        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

    def _build_action_bar(self):
        bar = tk.Frame(self, bg=theme.BG_MAIN, pady=10)
        bar.pack(fill="x", padx=20)

        btn_add = ttk.Button(
            bar,
            text="+ Register New Donor",
            style="Primary.TButton",
            command=self._open_register_modal
        )
        btn_add.pack(side="left", padx=(0, 10))

        btn_donate = ttk.Button(
            bar,
            text="🩸 Record Donation for Selected Donor",
            style="Success.TButton",
            command=self._record_donation_flow
        )
        btn_donate.pack(side="left")

        self.lbl_count = tk.Label(bar, text="", font=theme.FONT_SMALL_BOLD, bg=theme.BG_MAIN, fg=theme.TEXT_SECONDARY)
        self.lbl_count.pack(side="right")

    def refresh_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        query = self.entry_search.get()
        sel_group_str = self.cb_blood_filter.get()
        bg_filter = None if sel_group_str == "All" else BloodGroup.from_string(sel_group_str)
        only_elig = self.var_only_eligible.get()

        donors = self._donors.search_donors(
            query=query,
            blood_group=bg_filter,
            only_eligible=only_elig
        )

        for d in donors:
            status, reason = d.evaluate_eligibility()
            self.tree.insert(
                "",
                "end",
                values=(
                    d.id,
                    d.full_name,
                    d.blood_group.value,
                    d.age,
                    d.gender,
                    f"{d.weight_kg:.1f} kg",
                    d.contact_number,
                    d.city,
                    d.total_donations,
                    status.value,
                    reason
                )
            )

        self.lbl_count.config(text=f"Total Donors Displayed: {len(donors)}")

    def _open_register_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Register New Blood Donor")
        modal.geometry("520x620")
        modal.configure(bg=theme.BG_CARD)
        modal.transient(self)
        modal.grab_set()

        lbl_head = tk.Label(
            modal,
            text="Donor Clinical Registration Form",
            font=theme.FONT_HEADING,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY
        )
        lbl_head.pack(pady=(15, 10))

        form = tk.Frame(modal, bg=theme.BG_CARD, padx=25)
        form.pack(fill="both", expand=True)

        fields = [
            ("Donor ID:", "DNR-" + str(1000 + len(self._donors.get_all_donors()) + 1)),
            ("First Name:", ""),
            ("Last Name:", ""),
            ("Blood Group:", BloodGroup.O_POS.value),
            ("Age (18-65):", "25"),
            ("Gender:", "Male"),
            ("Weight in kg (≥50):", "65.0"),
            ("Contact Number:", "+91-"),
            ("Email Address:", "user@example.com"),
            ("City:", "Mumbai"),
            ("Medical Conditions:", "None")
        ]

        widgets = {}
        for i, (label_txt, default_val) in enumerate(fields):
            lbl = tk.Label(form, text=label_txt, font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD, anchor="w")
            lbl.grid(row=i, column=0, sticky="w", pady=4)

            if label_txt == "Blood Group:":
                ent = ttk.Combobox(form, values=[bg.value for bg in BloodGroup], state="readonly", width=25)
                ent.set(default_val)
            elif label_txt == "Gender:":
                ent = ttk.Combobox(form, values=["Male", "Female", "Other"], state="readonly", width=25)
                ent.set(default_val)
            else:
                ent = ttk.Entry(form, width=28)
                ent.insert(0, default_val)

            ent.grid(row=i, column=1, sticky="e", pady=4)
            widgets[label_txt] = ent

        def submit():
            try:
                donor_id = widgets["Donor ID:"].get().strip()
                fname = widgets["First Name:"].get().strip()
                lname = widgets["Last Name:"].get().strip()
                if not fname or not lname:
                    messagebox.showerror("Validation Error", "First and Last names are mandatory.", parent=modal)
                    return

                bg = BloodGroup.from_string(widgets["Blood Group:"].get())
                age = int(widgets["Age (18-65):"].get())
                gender = widgets["Gender:"].get()
                weight = float(widgets["Weight in kg (≥50):"].get())
                contact = widgets["Contact Number:"].get().strip()
                email = widgets["Email Address:"].get().strip()
                city = widgets["City:"].get().strip()
                med = widgets["Medical Conditions:"].get().strip()

                new_donor = Donor(
                    person_id=donor_id,
                    first_name=fname,
                    last_name=lname,
                    blood_group=bg,
                    contact_number=contact,
                    email=email,
                    age=age,
                    gender=gender,
                    weight_kg=weight,
                    last_donation_date=None,
                    total_donations=0,
                    medical_conditions=med,
                    city=city
                )

                self._donors.register_donor(new_donor)
                status, reason = new_donor.evaluate_eligibility()
                messagebox.showinfo(
                    "Registration Successful",
                    f"Donor {new_donor.full_name} registered successfully!\nStatus: {status.value}\n({reason})",
                    parent=modal
                )
                modal.destroy()
                self.refresh_data()
            except ValueError as ve:
                messagebox.showerror("Invalid Input", str(ve), parent=modal)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to register donor: {e}", parent=modal)

        btn_save = ttk.Button(modal, text="Save & Qualify Donor", style="Primary.TButton", command=submit)
        btn_save.pack(pady=15)

    def _record_donation_flow(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a donor from the table to record a donation.")
            return

        item = self.tree.item(selected[0])
        donor_id = item["values"][0]
        donor = self._donors.get_donor_by_id(donor_id)
        if not donor:
            return

        status, reason = donor.evaluate_eligibility()
        if status != DonorStatus.ELIGIBLE:
            messagebox.showerror(
                "Clinical Deferral",
                f"Cannot collect blood from {donor.full_name}.\nReason: {reason}",
                parent=self
            )
            return

        confirm = messagebox.askyesno(
            "Confirm Donation Collection",
            f"Record collection of 450ml Whole Blood from eligible donor:\n"
            f"Name: {donor.full_name} ({donor.blood_group.value})\n"
            f"This will add 1 new verified unit to the cold inventory.",
            parent=self
        )
        if not confirm:
            return

        # Generate barcoded unit ID
        existing_units = self._inventory.get_all_units()
        unit_id = f"UNT-{len(existing_units) + 5001}"
        new_unit = BloodUnit(
            unit_id=unit_id,
            blood_group=donor.blood_group,
            donor_id=donor.id,
            component_type=BloodComponent.WHOLE_BLOOD,
            volume_ml=450.0,
            collected_date=date.today(),
            storage_location="Vault Alpha - Intake Tray"
        )

        self._inventory.add_unit(new_unit)
        donation_rec = self._donors.record_donation(
            donor_id=donor.id,
            unit_id=unit_id,
            donation_date=date.today(),
            facility="Central Blood Bank Mobile Unit"
        )

        messagebox.showinfo(
            "Donation Recorded",
            f"Donation successfully processed!\n"
            f"• Unit ID: {unit_id}\n"
            f"• Blood Group: {new_unit.blood_group.value}\n"
            f"• Shelf Life: Valid until {new_unit.expiry_date.isoformat()} (35 days)\n"
            f"• Donor's new total donations: {donor.total_donations}",
            parent=self
        )
        self.refresh_data()
