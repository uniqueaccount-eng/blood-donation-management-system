"""
ui/dashboard_view.py
Interactive Executive Dashboard displaying real-time metrics,
blood inventory levels by group, expiry warnings, and emergency requisitions.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, Optional
from models.enums import BloodGroup, RequestUrgency, RequestStatus
from services.inventory_manager import InventoryManager
from services.donor_service import DonorService
from services.request_service import RequestService
import ui.theme as theme


class DashboardView(tk.Frame):
    """
    Main Executive Dashboard View.
    Renders high-level clinical statistics and instant action prompts.
    """

    def __init__(
        self,
        parent: tk.Widget,
        inventory_mgr: InventoryManager,
        donor_svc: DonorService,
        request_svc: RequestService,
        on_navigate: Optional[Callable[[int], None]] = None
    ):
        super().__init__(parent, bg=theme.BG_MAIN)
        self._inventory = inventory_mgr
        self._donors = donor_svc
        self._requests = request_svc
        self._on_navigate = on_navigate

        # Build UI layout
        self._build_header()
        self._build_kpi_cards()
        self._build_stock_overview()
        self._build_action_alerts()

        # Register observer on inventory
        self._inventory.register_observer(self.refresh_data)

    def _build_header(self):
        header_frame = tk.Frame(self, bg=theme.BG_MAIN)
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title_lbl = tk.Label(
            header_frame,
            text="Blood Bank Overview Dashboard",
            font=theme.FONT_TITLE,
            bg=theme.BG_MAIN,
            fg=theme.TEXT_PRIMARY
        )
        title_lbl.pack(side="left")

        # SDG Tag
        sdg_badge = tk.Label(
            header_frame,
            text="Mapped to SDG 3: Good Health & Well-Being",
            font=theme.FONT_SMALL_BOLD,
            bg="#DCFCE7",
            fg="#166534",
            padx=10,
            pady=4,
            relief="solid",
            bd=1
        )
        sdg_badge.pack(side="right")

    def _build_kpi_cards(self):
        kpi_container = tk.Frame(self, bg=theme.BG_MAIN)
        kpi_container.pack(fill="x", padx=20, pady=10)
        kpi_container.columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        self.card_units = self._create_kpi_card(
            kpi_container, 0, "Available Units", "0", "Units in Storage", theme.INFO_COLOR
        )
        self.card_donors = self._create_kpi_card(
            kpi_container, 1, "Registered Donors", "0", "Total in Database", theme.SUCCESS_COLOR
        )
        self.card_pending = self._create_kpi_card(
            kpi_container, 2, "Pending Requests", "0", "Hospital Demands", theme.DANGER_COLOR
        )
        self.card_expiring = self._create_kpi_card(
            kpi_container, 3, "Expiring in ≤ 7 Days", "0", "Needs Priority Dispatch", theme.WARNING_COLOR
        )

    def _create_kpi_card(self, parent, col, title, value, subtitle, accent_color):
        card = tk.Frame(parent, bg=theme.BG_CARD, bd=1, relief="solid")
        card.grid(row=0, column=col, padx=6, sticky="nsew")

        # Top accent bar
        accent = tk.Frame(card, bg=accent_color, height=4)
        accent.pack(fill="x")

        # Inner padding
        inner = tk.Frame(card, bg=theme.BG_CARD, padx=12, pady=10)
        inner.pack(fill="both", expand=True)

        lbl_title = tk.Label(inner, text=title, font=theme.FONT_SMALL_BOLD, bg=theme.BG_CARD, fg=theme.TEXT_SECONDARY)
        lbl_title.pack(anchor="w")

        lbl_val = tk.Label(inner, text=value, font=theme.FONT_STAT_VAL, bg=theme.BG_CARD, fg=theme.TEXT_PRIMARY)
        lbl_val.pack(anchor="w", pady=(2, 2))

        lbl_sub = tk.Label(inner, text=subtitle, font=theme.FONT_SMALL, bg=theme.BG_CARD, fg=theme.TEXT_MUTED)
        lbl_sub.pack(anchor="w")

        return lbl_val

    def _build_stock_overview(self):
        stock_frame = tk.LabelFrame(
            self,
            text=" Real-Time Blood Group Inventory Levels ",
            font=theme.FONT_HEADING,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY,
            bd=1,
            relief="solid",
            padx=15,
            pady=12
        )
        stock_frame.pack(fill="x", padx=20, pady=10)

        self._stock_labels = {}
        cols = 8
        for i, bg in enumerate(BloodGroup):
            col_frame = tk.Frame(stock_frame, bg=theme.BG_CARD, bd=1, relief="ridge", padx=8, pady=8)
            col_frame.grid(row=0, column=i, padx=5, pady=4, sticky="nsew")
            stock_frame.columnconfigure(i, weight=1)

            lbl_bg = tk.Label(
                col_frame,
                text=bg.value,
                font=(theme.FONT_FAMILY, 13, "bold"),
                bg=theme.BG_CARD,
                fg=theme.PRIMARY_COLOR
            )
            lbl_bg.pack()

            lbl_cnt = tk.Label(
                col_frame,
                text="0 units",
                font=theme.FONT_BODY_BOLD,
                bg=theme.BG_CARD,
                fg=theme.TEXT_PRIMARY
            )
            lbl_cnt.pack(pady=(2, 4))

            lbl_status = tk.Label(
                col_frame,
                text="Normal",
                font=theme.FONT_SMALL,
                bg="#E2E8F0",
                fg=theme.TEXT_SECONDARY,
                padx=4,
                pady=2
            )
            lbl_status.pack()

            self._stock_labels[bg] = (lbl_cnt, lbl_status)

    def _build_action_alerts(self):
        bottom_container = tk.Frame(self, bg=theme.BG_MAIN)
        bottom_container.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        bottom_container.columnconfigure(0, weight=3)
        bottom_container.columnconfigure(1, weight=2)

        # Urgent Requisitions Panel
        req_frame = tk.LabelFrame(
            bottom_container,
            text=" Urgent Hospital Requisitions ",
            font=theme.FONT_HEADING,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY,
            bd=1,
            relief="solid",
            padx=10,
            pady=10
        )
        req_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        cols = ("Req ID", "Patient", "Hospital", "Group", "Units", "Urgency")
        self._tree_urgent = ttk.Treeview(req_frame, columns=cols, show="headings", height=5)
        for c in cols:
            self._tree_urgent.heading(c, text=c)
            width = 65 if c in ("Req ID", "Group", "Units") else 105
            self._tree_urgent.column(c, width=width, anchor="center")

        self._tree_urgent.pack(fill="both", expand=True, side="left")
        scroll = ttk.Scrollbar(req_frame, orient="vertical", command=self._tree_urgent.yview)
        self._tree_urgent.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")

        # Quick Links & Expiry Warnings Panel
        alert_frame = tk.LabelFrame(
            bottom_container,
            text=" Expiry & Shortage Alerts ",
            font=theme.FONT_HEADING,
            bg=theme.BG_CARD,
            fg=theme.TEXT_PRIMARY,
            bd=1,
            relief="solid",
            padx=12,
            pady=10
        )
        alert_frame.grid(row=0, column=1, sticky="nsew")

        self._lbl_alerts = tk.Label(
            alert_frame,
            text="Loading alerts...",
            font=theme.FONT_BODY,
            bg=theme.BG_CARD,
            fg=theme.TEXT_SECONDARY,
            justify="left",
            wraplength=280
        )
        self._lbl_alerts.pack(anchor="w", fill="both", expand=True)

        btn_row = tk.Frame(alert_frame, bg=theme.BG_CARD)
        btn_row.pack(fill="x", pady=(10, 0))

        btn_go_req = ttk.Button(
            btn_row,
            text="Manage Requisitions",
            style="Primary.TButton",
            command=lambda: self._on_navigate(3) if self._on_navigate else None
        )
        btn_go_req.pack(side="left", fill="x", expand=True, padx=(0, 4))

        btn_go_inv = ttk.Button(
            btn_row,
            text="View Inventory",
            style="Secondary.TButton",
            command=lambda: self._on_navigate(2) if self._on_navigate else None
        )
        btn_go_inv.pack(side="right", fill="x", expand=True, padx=(4, 0))

    def refresh_data(self):
        """Refreshes all displayed numbers and tables from models/services."""
        # 1. Update KPI Cards
        avail_units = self._inventory.get_available_units()
        donors = self._donors.get_all_donors()
        pending = self._requests.get_pending_requests()
        expiring = self._inventory.get_units_expiring_soon(within_days=7)

        self.card_units.config(text=str(len(avail_units)))
        self.card_donors.config(text=str(len(donors)))
        self.card_pending.config(text=str(len(pending)))
        self.card_expiring.config(text=str(len(expiring)))

        # 2. Update Blood Group Matrix
        stock_counts = self._inventory.get_stock_counts()
        for bg, (lbl_cnt, lbl_status) in self._stock_labels.items():
            count = stock_counts.get(bg, 0)
            lbl_cnt.config(text=f"{count} unit(s)")
            if count == 0:
                lbl_status.config(text="OUT OF STOCK", bg="#FEE2E2", fg=theme.DANGER_COLOR)
            elif count < self._inventory.CRITICAL_STOCK_THRESHOLD:
                lbl_status.config(text="LOW STOCK", bg="#FEF3C7", fg="#B45309")
            else:
                lbl_status.config(text="ADEQUATE", bg="#DCFCE7", fg="#15803D")

        # 3. Update Urgent Requisitions Table
        for row in self._tree_urgent.get_children():
            self._tree_urgent.delete(row)

        for req in pending[:8]:
            self._tree_urgent.insert(
                "",
                "end",
                values=(
                    req.request_id,
                    req.recipient_name,
                    req.hospital_name,
                    req.blood_group.value,
                    req.units_requested,
                    req.urgency.value
                )
            )

        # 4. Update Expiry and Shortage Alerts Text
        shortages = self._inventory.get_critical_shortages()
        alert_lines = []
        if shortages:
            shortage_str = ", ".join(bg.value for bg in shortages)
            alert_lines.append(f"⚠️ Critical shortage in: {shortage_str}")
        else:
            alert_lines.append("✅ All blood group reserves meet minimum safety thresholds.")

        if expiring:
            alert_lines.append(f"⏱️ {len(expiring)} unit(s) expiring within 7 days. FIFO dispatch active.")
        else:
            alert_lines.append("✅ No immediate blood unit expirations detected.")

        self._lbl_alerts.config(text="\n\n".join(alert_lines))
