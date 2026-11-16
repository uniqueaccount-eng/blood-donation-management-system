"""
ui/request_view.py
Requisition management panel with automated biological compatibility matching,
FIFO dispatching, and emergency priority queuing.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from typing import Optional
from models.enums import BloodGroup, BloodComponent, RequestUrgency, RequestStatus
from models.request import BloodRequest
from services.request_service import RequestService
from services.compatibility import BloodCompatibilityService
import ui.theme as theme


class RequestView(tk.Frame):
    """
    Hospital requisition fulfillment view.
    Automates cross-matching and life-saving priority dispatching.
    """

    def __init__(
        self,
        parent: tk.Widget,
        request_svc: RequestService,
        compatibility_svc: BloodCompatibilityService
    ):
        super().__init__(parent, bg=theme.BG_MAIN)
        self._requests = request_svc
        self._compatibility = compatibility_svc

        self._build_header()
        self._build_filters()
        self._build_table()
        self._build_action_bar()

    def _build_header(self):
        header = tk.Frame(self, bg=theme.BG_MAIN)
        header.pack(fill="x", padx=20, pady=(15, 5))

        title = tk.Label(
            header,
            text="Hospital Requisitions & Transfusion Matching",
            font=theme.FONT_TITLE,
            bg=theme.BG_MAIN,
            fg=theme.TEXT_PRIMARY
        )
        title.pack(side="left")

        badge = tk.Label(
            header,
            text="Automated ABO/Rh Cross-Match Algorithm Enabled",
            font=theme.FONT_SMALL_BOLD,
            bg="#FEF3C7",
            fg="#92400E",
            padx=8,
            pady=3,
            relief="solid",
            bd=1
        )
        badge.pack(side="right")

    def _build_filters(self):
        bar = tk.Frame(self, bg=theme.BG_CARD, bd=1, relief="solid", padx=12, pady=10)
        bar.pack(fill="x", padx=20, pady=8)

        # Status Filter
        tk.Label(bar, text="Status:", font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD).pack(side="left", padx=(0, 4))
        self.cb_status = ttk.Combobox(
            bar,
            values=["All", "Pending Only"] + [s.value for s in RequestStatus],
            state="readonly",
            width=14
        )
        self.cb_status.current(1)  # Default: Pending Only
        self.cb_status.pack(side="left", padx=(0, 15))
        self.cb_status.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        # Urgency Filter
        tk.Label(bar, text="Urgency:", font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD).pack(side="left", padx=(0, 4))
        self.cb_urgency = ttk.Combobox(
            bar,
            values=["All"] + [u.value for u in RequestUrgency],
            state="readonly",
            width=18
        )
        self.cb_urgency.current(0)
        self.cb_urgency.pack(side="left", padx=(0, 15))
        self.cb_urgency.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        btn_refresh = ttk.Button(bar, text="Refresh Queue", style="Secondary.TButton", command=self.refresh_data)
        btn_refresh.pack(side="right")

    def _build_table(self):
        table_frame = tk.Frame(self, bg=theme.BG_CARD, bd=1, relief="solid")
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols = (
            "Req ID", "Urgency", "Patient", "Hospital", "Group",
            "Units", "Component", "Requested At", "Status", "Allocated Units", "Notes"
        )
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", selectmode="browse")

        col_widths = {
            "Req ID": 75, "Urgency": 110, "Patient": 120, "Hospital": 140, "Group": 60,
            "Units": 55, "Component": 130, "Requested At": 120, "Status": 85, "Allocated Units": 110, "Notes": 160
        }
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=col_widths.get(c, 80), anchor="center")
        self.tree.column("Patient", anchor="w")
        self.tree.column("Hospital", anchor="w")
        self.tree.column("Notes", anchor="w")

        # Color tags for urgency
        self.tree.tag_configure("critical", background="#FEE2E2", foreground=theme.DANGER_COLOR)
        self.tree.tag_configure("urgent", background="#FEF3C7", foreground="#92400E")
        self.tree.tag_configure("fulfilled", background="#DCFCE7", foreground="#15803D")

        y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.pack(side="left", fill="both", expand=True)
        y_scroll.pack(side="right", fill="y")
        x_scroll.pack(side="bottom", fill="x")

    def _build_action_bar(self):
        bar = tk.Frame(self, bg=theme.BG_MAIN, pady=10)
        bar.pack(fill="x", padx=20)

        btn_create = ttk.Button(
            bar,
            text="+ Create Blood Requisition",
            style="Primary.TButton",
            command=self._open_create_modal
        )
        btn_create.pack(side="left", padx=(0, 10))

        btn_fulfill = ttk.Button(
            bar,
            text="⚡ Match & Fulfill Selected Requisition",
            style="Success.TButton",
            command=self._fulfill_flow
        )
        btn_fulfill.pack(side="left", padx=(0, 10))

        btn_cancel = ttk.Button(
            bar,
            text="Cancel Request",
            style="Secondary.TButton",
            command=self._cancel_flow
        )
        btn_cancel.pack(side="left")

        self.lbl_info = tk.Label(bar, text="", font=theme.FONT_SMALL_BOLD, bg=theme.BG_MAIN, fg=theme.TEXT_SECONDARY)
        self.lbl_info.pack(side="right")

    def refresh_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        requests = self._requests.get_all_requests()

        status_val = self.cb_status.get()
        if status_val == "Pending Only":
            requests = [r for r in requests if r.status == RequestStatus.PENDING]
        elif status_val != "All":
            requests = [r for r in requests if r.status.value == status_val]

        urg_val = self.cb_urgency.get()
        if urg_val != "All":
            requests = [r for r in requests if r.urgency.value == urg_val]

        for r in requests:
            tag = ""
            if r.status == RequestStatus.FULFILLED:
                tag = "fulfilled"
            elif r.urgency == RequestUrgency.CRITICAL:
                tag = "critical"
            elif r.urgency == RequestUrgency.URGENT:
                tag = "urgent"

            alloc_str = ", ".join(r.allocated_unit_ids) if r.allocated_unit_ids else "-"
            date_str = r.request_date.strftime("%Y-%m-%d %H:%M")

            self.tree.insert(
                "",
                "end",
                values=(
                    r.request_id,
                    r.urgency.value,
                    r.recipient_name,
                    r.hospital_name,
                    r.blood_group.value,
                    r.units_requested,
                    r.component_type.value,
                    date_str,
                    r.status.value,
                    alloc_str,
                    r.notes
                ),
                tags=(tag,)
            )

        self.lbl_info.config(text=f"Total Requests: {len(requests)}")

    def _open_create_modal(self):
        modal = tk.Toplevel(self)
        modal.title("Create Hospital Blood Requisition")
        modal.geometry("500x560")
        modal.configure(bg=theme.BG_CARD)
        modal.transient(self)
        modal.grab_set()

        lbl_head = tk.Label(
            modal,
            text="Hospital Emergency Requisition Form",
            font=theme.FONT_HEADING,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY
        )
        lbl_head.pack(pady=12)

        form = tk.Frame(modal, bg=theme.BG_CARD, padx=25)
        form.pack(fill="both", expand=True)

        existing = self._requests.get_all_requests()
        next_id = f"REQ-{len(existing) + 8001}"

        fields = [
            ("Request ID:", next_id),
            ("Patient Name:", ""),
            ("Patient ID:", f"RCP-{len(existing) + 2001}"),
            ("Blood Group Needed:", BloodGroup.O_NEG.value),
            ("Units Requested:", "1"),
            ("Urgency Priority:", RequestUrgency.CRITICAL.value),
            ("Component:", BloodComponent.WHOLE_BLOOD.value),
            ("Hospital / Center:", "Apex Trauma Care"),
            ("Clinical Diagnosis / Notes:", "Severe acute trauma hemorrhage")
        ]

        widgets = {}
        for i, (label_txt, def_val) in enumerate(fields):
            lbl = tk.Label(form, text=label_txt, font=theme.FONT_BODY_BOLD, bg=theme.BG_CARD, anchor="w")
            lbl.grid(row=i, column=0, sticky="w", pady=5)

            if label_txt == "Blood Group Needed:":
                ent = ttk.Combobox(form, values=[bg.value for bg in BloodGroup], state="readonly", width=24)
                ent.set(def_val)
            elif label_txt == "Urgency Priority:":
                ent = ttk.Combobox(form, values=[u.value for u in RequestUrgency], state="readonly", width=24)
                ent.set(def_val)
            elif label_txt == "Component:":
                ent = ttk.Combobox(form, values=[c.value for c in BloodComponent], state="readonly", width=24)
                ent.set(def_val)
            else:
                ent = ttk.Entry(form, width=27)
                ent.insert(0, def_val)

            ent.grid(row=i, column=1, sticky="e", pady=5)
            widgets[label_txt] = ent

        def submit():
            try:
                rid = widgets["Request ID:"].get().strip()
                pname = widgets["Patient Name:"].get().strip()
                if not pname:
                    messagebox.showerror("Error", "Patient Name cannot be blank.", parent=modal)
                    return
                pid = widgets["Patient ID:"].get().strip()
                bg = BloodGroup.from_string(widgets["Blood Group Needed:"].get())
                units = int(widgets["Units Requested:"].get())
                urg_str = widgets["Urgency Priority:"].get()
                urg = next(u for u in RequestUrgency if u.value == urg_str)
                comp_str = widgets["Component:"].get()
                comp = next(c for c in BloodComponent if c.value == comp_str)
                hosp = widgets["Hospital / Center:"].get().strip()
                notes = widgets["Clinical Diagnosis / Notes:"].get().strip()

                req = BloodRequest(
                    request_id=rid,
                    recipient_id=pid,
                    recipient_name=pname,
                    blood_group=bg,
                    units_requested=units,
                    hospital_name=hosp,
                    urgency=urg,
                    component_type=comp,
                    notes=notes
                )
                self._requests.create_request(req)
                messagebox.showinfo("Requisition Created", f"Request {rid} enqueued with priority {urg.value}.", parent=modal)
                modal.destroy()
                self.refresh_data()
            except ValueError as ve:
                messagebox.showerror("Validation Error", str(ve), parent=modal)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to submit: {e}", parent=modal)

        btn_sub = ttk.Button(modal, text="Submit Requisition", style="Primary.TButton", command=submit)
        btn_sub.pack(pady=15)

    def _fulfill_flow(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a pending request from the table to fulfill.")
            return

        item = self.tree.item(selected[0])
        req_id = item["values"][0]
        req = self._requests.get_request_by_id(req_id)
        if not req:
            return

        if req.status != RequestStatus.PENDING:
            messagebox.showinfo("Status Notice", f"This requisition is already {req.status.value}.", parent=self)
            return

        # Show compatible groups for educational transparency
        comp_groups = self._compatibility.get_compatible_donor_groups(req.blood_group, req.component_type)
        comp_str = ", ".join(bg.value for bg in comp_groups)

        confirm = messagebox.askyesno(
            "Execute Cross-Match & Fulfillment",
            f"Cross-match details for Requisition {req.request_id}:\n\n"
            f"• Patient: {req.recipient_name}\n"
            f"• Required Group: {req.blood_group.value}\n"
            f"• Compatible Donor Blood Groups: [{comp_str}]\n"
            f"• Required Units: {req.units_requested}\n"
            f"• Dispatch Algorithm: FIFO (Earliest Expiry)\n\n"
            f"Proceed with automatic allocation?",
            parent=self
        )
        if not confirm:
            return

        success, msg, unit_ids = self._requests.match_and_fulfill(req_id)
        if success:
            messagebox.showinfo("Fulfillment Successful", f"✅ {msg}", parent=self)
        else:
            messagebox.showerror("Inventory Insufficient", f"❌ {msg}", parent=self)

        self.refresh_data()

    def _cancel_flow(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a request to cancel.")
            return

        req_id = self.tree.item(selected[0])["values"][0]
        confirm = messagebox.askyesno("Cancel Request", f"Are you sure you want to cancel request {req_id}?", parent=self)
        if confirm:
            self._requests.cancel_request(req_id, reason="Cancelled by coordinator")
            self.refresh_data()
