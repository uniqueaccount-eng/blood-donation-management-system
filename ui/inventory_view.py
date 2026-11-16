"""
ui/inventory_view.py
Inventory control table tracking barcoded blood units, cold-chain storage locations,
shelf-life days remaining, and biohazard expiry disposal.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from typing import Optional
from models.enums import BloodGroup, BloodComponent, UnitStatus
from models.blood_unit import BloodUnit
from services.inventory_manager import InventoryManager
import ui.theme as theme


class InventoryView(tk.Frame):
    """
    Manages cold vault stock, component separations, and shelf life monitoring.
    """

    def __init__(self, parent: tk.Widget, inventory_mgr: InventoryManager):
        super().__init__(parent, bg=theme.BG_MAIN)
        self._inventory = inventory_mgr

        self._build_header()
        self._build_filters()
        self._build_table()
        self._build_action_bar()

    def _build_header(self):
        header = tk.Frame(self, bg=theme.BG_MAIN)
        header.pack(fill="x", padx=20, pady=(15, 5))

        title = tk.Label(
            header,
            text="Blood Cold Storage & Inventory Tracker",
            font=theme.FONT_TITLE,
            bg=theme.BG_MAIN,
            fg=theme.TEXT_PRIMARY
        )
        title.pack(side="left")

        sdg_note = tk.Label(
            header,
            text="SDG 12 & 3: FIFO Scheduling active to eliminate blood wastage",
            font=theme.FONT_SMALL_BOLD,
            bg="#E0F2FE",
            fg="#0369A1",
            padx=8,
            pady=3,
            relief="solid",
            bd=1
        )
        sdg_note.pack(side="right")

    def _build_filters(self):
        bar = tk.Frame(self, bg=theme.BG_CARD, bd=1, relief="solid", padx=12, pady=10)
        bar.pack(fill="x", padx=20, pady=8)

        # Blood Group Filter
        tk.Label(bar, text="Group:", font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD).pack(side="left", padx=(0, 4))
        self.cb_bg = ttk.Combobox(bar, values=["All"] + [bg.value for bg in BloodGroup], state="readonly", width=8)
        self.cb_bg.current(0)
        self.cb_bg.pack(side="left", padx=(0, 15))
        self.cb_bg.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        # Component Filter
        tk.Label(bar, text="Component:", font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD).pack(side="left", padx=(0, 4))
        self.cb_comp = ttk.Combobox(bar, values=["All"] + [c.value for c in BloodComponent], state="readonly", width=18)
        self.cb_comp.current(0)
        self.cb_comp.pack(side="left", padx=(0, 15))
        self.cb_comp.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        # Status Filter
        tk.Label(bar, text="Status:", font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD).pack(side="left", padx=(0, 4))
        self.cb_status = ttk.Combobox(bar, values=["All"] + [s.value for s in UnitStatus], state="readonly", width=12)
        self.cb_status.current(0)
        self.cb_status.pack(side="left", padx=(0, 15))
        self.cb_status.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        btn_refresh = ttk.Button(bar, text="Audit Expiries", style="Secondary.TButton", command=self._audit_expiries)
        btn_refresh.pack(side="right")

    def _build_table(self):
        table_frame = tk.Frame(self, bg=theme.BG_CARD, bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols = (
            "Unit ID", "Group", "Component", "Volume", "Donor ID",
            "Collected", "Expires On", "Days Left", "Status", "Storage Location"
        )
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        col_widths = {
            "Unit ID": 80, "Group": 60, "Component": 160, "Volume": 70, "Donor ID": 80,
            "Collected": 90, "Expires On": 90, "Days Left": 75, "Status": 90, "Storage Location": 150
        }
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 85), anchor="center")
        self.tree.column("Storage Location", anchor="w")

        # Configure row color tags for expiry warnings
        self.tree.tag_configure("expired", background="#FEE2E2", foreground=theme.DANGER_COLOR)
        self.tree.tag_configure("expiring_soon", background="#FEF3C7", foreground="#92400E")
        self.tree.tag_configure("transfused", background="#F1F5F9", foreground=theme.TEXT_MUTED)

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

    def _build_action_bar(self):
        bar = tk.Frame(self, bg=theme.BG_MAIN, pady=10)
        bar.pack(fill="x", padx=20)

        btn_add = ttk.Button(bar, text="+ Add Blood Unit Manually", style="Primary.TButton", command=self._open_add_modal)
        btn_add.pack(side="left", padx=(0, 10))

        btn_discard = ttk.Button(
            bar,
            text="⚠️ Inspect & Biohazard Disposal",
            style="Secondary.TButton",
            command=self._discard_expired
        )
        btn_discard.pack(side="left")

        self.lbl_summary = tk.Label(bar, text="", font=theme.FONT_SMALL_BOLD, bg=theme.BG_MAIN, fg=theme.TEXT_SECONDARY)
        self.lbl_summary.pack(side="right")

    def refresh_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        units = self._inventory.get_all_units()

        # Apply Filters
        bg_filter = self.cb_bg.get()
        if bg_filter != "All":
            units = [u for u in units if u.blood_group.value == bg_filter]

        comp_filter = self.cb_comp.get()
        if comp_filter != "All":
            units = [u for u in units if u.component_type.value == comp_filter]

        status_filter = self.cb_status.get()
        if status_filter != "All":
            units = [u for u in units if u.status.value == status_filter]

        today = date.today()
        # Sort FIFO: Available units expiring earliest first
        units.sort(key=lambda u: (0 if u.status == UnitStatus.AVAILABLE else 1, u.expiry_date))

        for u in units:
            days_left = u.days_until_expiry(today)
            tag = ""
            if u.status == UnitStatus.EXPIRED or days_left < 0:
                tag = "expired"
                days_txt = f"EXPIRED ({abs(days_left)}d ago)"
            elif u.status == UnitStatus.TRANSFUSED:
                tag = "transfused"
                days_txt = "-"
            elif days_left <= 7:
                tag = "expiring_soon"
                days_txt = f"⚠️ {days_left} day(s)"
            else:
                days_txt = f"{days_left} day(s)"

            self.tree.insert(
                "",
                "end",
                values=(
                    u.unit_id,
                    u.blood_group.value,
                    u.component_type.value,
                    f"{u.volume_ml:.0f} ml",
                    u.donor_id,
                    u.collected_date.isoformat(),
                    u.expiry_date.isoformat(),
                    days_txt,
                    u.status.value,
                    u.storage_location
                ),
                tags=(tag,)
            )

        avail_count = sum(1 for u in units if u.status == UnitStatus.AVAILABLE)
        self.lbl_summary.config(text=f"Total Shown: {len(units)} | Currently Available: {avail_count}")

    def _audit_expiries(self):
        count = self._inventory.refresh_expiries()
        self.refresh_data()
        messagebox.showinfo(
            "Expiry Audit Complete",
            f"Automated cold storage audit finished.\n"
            f"Detected and updated {count} expired unit(s) to EXPIRED status.",
            parent=self
        )

    def _discard_expired(self):
        expired = [u for u in self._inventory.get_all_units() if u.status == UnitStatus.EXPIRED]
        if not expired:
            messagebox.showinfo("Safe Inventory", "No expired units currently in storage.", parent=self)
            return

        confirm = messagebox.askyesno(
            "Confirm Biohazard Waste Disposal",
            f"Found {len(expired)} expired blood unit(s).\n"
            f"Units: {', '.join(u.unit_id for u in expired[:5])}{'...' if len(expired) > 5 else ''}\n"
            f"Confirm documentation for hospital incinerator biohazard protocol?",
            parent=self
        )
        if confirm:
            self._inventory.discard_expired_units()
            messagebox.showinfo("Disposal Logged", f"{len(expired)} expired units processed for disposal.", parent=self)
            self.refresh_data()

    def _open_add_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Add Blood Unit to Cold Storage")
        modal.geometry("450x450")
        modal.configure(bg=theme.BG_CARD)
        modal.transient(self)
        modal.grab_set()

        lbl_head = tk.Label(
            modal,
            text="Blood Unit Cold Chain Intake",
            font=theme.FONT_HEADING,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY
        )
        lbl_head.pack(pady=12)

        form = tk.Frame(modal, bg=theme.BG_CARD, padx=20)
        form.pack(fill="both", expand=True)

        existing = self._inventory.get_all_units()
        next_id = f"UNT-{len(existing) + 5001}"

        fields = [
            ("Unit ID:", next_id),
            ("Blood Group:", BloodGroup.O_POS.value),
            ("Donor ID:", "DNR-1001"),
            ("Component:", BloodComponent.WHOLE_BLOOD.value),
            ("Volume (ml):", "450.0"),
            ("Storage Location:", "Vault Alpha - Shelf 1")
        ]

        widgets = {}
        for i, (label_txt, def_val) in enumerate(fields):
            lbl = tk.Label(form, text=label_txt, font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD, anchor="w")
            lbl.grid(row=i, column=0, sticky="w", pady=6)

            if label_txt == "Blood Group:":
                ent = ttk.Combobox(form, values=[bg.value for bg in BloodGroup], state="readonly", width=22)
                ent.set(def_val)
            elif label_txt == "Component:":
                ent = ttk.Combobox(form, values=[c.value for c in BloodComponent], state="readonly", width=22)
                ent.set(def_val)
            else:
                ent = ttk.Entry(form, width=25)
                ent.insert(0, def_val)

            ent.grid(row=i, column=1, sticky="e", pady=6)
            widgets[label_txt] = ent

        def save():
            try:
                uid = widgets["Unit ID:"].get().strip()
                bg = BloodGroup.from_string(widgets["Blood Group:"].get())
                donor_id = widgets["Donor ID:"].get().strip()
                comp_str = widgets["Component:"].get()
                comp = next(c for c in BloodComponent if c.value == comp_str)
                vol = float(widgets["Volume (ml):"].get())
                loc = widgets["Storage Location:"].get().strip()

                unit = BloodUnit(
                    unit_id=uid,
                    blood_group=bg,
                    donor_id=donor_id,
                    component_type=comp,
                    volume_ml=vol,
                    collected_date=date.today(),
                    storage_location=loc
                )
                self._inventory.add_unit(unit)
                messagebox.showinfo("Unit Stored", f"Unit {uid} stored. Expiry set to {unit.expiry_date.isoformat()}.", parent=modal)
                modal.destroy()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add unit: {e}", parent=modal)

        btn_save = ttk.Button(modal, text="Add to Cold Inventory", style="Primary.TButton", command=save)
        btn_save.pack(pady=15)
