"""
ui/app.py
Main graphical user interface application window.
Hosts the navigation notebook, coordinates views, and orchestrates live updates.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
from storage.json_storage import JSONStorage
from services.inventory_manager import InventoryManager
from services.donor_service import DonorService
from services.compatibility import BloodCompatibilityService
from services.request_service import RequestService
import ui.theme as theme
from ui.dashboard_view import DashboardView
from ui.donor_view import DonorView
from ui.inventory_view import InventoryView
from ui.request_view import RequestView
from ui.analytics_view import AnalyticsView


class BloodDonationApp(tk.Tk):
    """
    Main Application Window for the Blood Donation Management System.
    """

    def __init__(self, data_directory: str):
        super().__init__()
        self.title("Blood Donation Management System - OOP Project")
        self.geometry("1180x740")
        self.minsize(1000, 650)
        self.configure(bg=theme.BG_MAIN)

        # Initialize storage and service layers
        self._storage = JSONStorage(data_directory)
        self._inventory_mgr = InventoryManager(self._storage)
        self._donor_svc = DonorService(self._storage)
        self._compat_svc = BloodCompatibilityService()
        self._request_svc = RequestService(self._storage, self._inventory_mgr, self._compat_svc)

        # Apply global styling
        theme.configure_app_styles(self)

        # Build UI elements
        self._build_top_brand_bar()
        self._build_notebook()
        self._build_status_bar()

        # Initial refresh
        self.after(100, self._initial_load)

    def _build_top_brand_bar(self):
        brand_frame = tk.Frame(self, bg=theme.PRIMARY_COLOR, height=60, padx=20, pady=8)
        brand_frame.pack(fill="x", side="top")

        left_brand = tk.Frame(brand_frame, bg=theme.PRIMARY_COLOR)
        left_brand.pack(side="left")

        lbl_icon = tk.Label(
            left_brand,
            text="🩸",
            font=(theme.FONT_FAMILY, 20),
            bg=theme.PRIMARY_COLOR,
            fg="#FFFFFF"
        )
        lbl_icon.pack(side="left", padx=(0, 10))

        title_box = tk.Frame(left_brand, bg=theme.PRIMARY_COLOR)
        title_box.pack(side="left")

        lbl_title = tk.Label(
            title_box,
            text="Blood Donation Management System",
            font=(theme.FONT_FAMILY, 15, "bold"),
            bg=theme.PRIMARY_COLOR,
            fg="#FFFFFF"
        )
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(
            title_box,
            text="2nd Year OOP Project - Mapped to SDG 3 (Good Health and Well-Being)",
            font=(theme.FONT_FAMILY, 9),
            bg=theme.PRIMARY_COLOR,
            fg="#FCA5A5"
        )
        lbl_sub.pack(anchor="w")

        # Right side info
        right_box = tk.Frame(brand_frame, bg=theme.PRIMARY_COLOR)
        right_box.pack(side="right")

        lbl_course = tk.Label(
            right_box,
            text="Author: uniqueaccount-eng",
            font=theme.FONT_SMALL_BOLD,
            bg="#991B1B",
            fg="#FEE2E2",
            padx=10,
            pady=4,
            relief="solid",
            bd=1
        )
        lbl_course.pack(side="top", anchor="e")

    def _build_notebook(self):
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=12, pady=(8, 0))

        # Instantiate Subviews
        self.view_dashboard = DashboardView(
            self.notebook,
            self._inventory_mgr,
            self._donor_svc,
            self._request_svc,
            on_navigate=self.switch_to_tab
        )
        self.view_donors = DonorView(
            self.notebook,
            self._donor_svc,
            self._inventory_mgr
        )
        self.view_inventory = InventoryView(
            self.notebook,
            self._inventory_mgr
        )
        self.view_requests = RequestView(
            self.notebook,
            self._request_svc,
            self._compat_svc
        )
        self.view_analytics = AnalyticsView(
            self.notebook,
            self._inventory_mgr,
            self._donor_svc,
            self._request_svc
        )

        # Add Tabs
        self.notebook.add(self.view_dashboard, text="  📊 Operations Dashboard  ")
        self.notebook.add(self.view_donors, text="  👥 Donors & Eligibility  ")
        self.notebook.add(self.view_inventory, text="  🩸 Cold Inventory & Expiries  ")
        self.notebook.add(self.view_requests, text="  🚑 Hospital Requisitions  ")
        self.notebook.add(self.view_analytics, text="  🎯 SDG 3 & Academic Mapping  ")

        # Listen to tab change events to trigger fresh loads
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

    def _build_status_bar(self):
        status_frame = tk.Frame(self, bg="#E2E8F0", height=24, padx=15)
        status_frame.pack(fill="x", side="bottom")

        lbl_status = tk.Label(
            status_frame,
            text="System Ready | Storage: JSON Files | Compatibility Engine: ABO/Rh Active",
            font=theme.FONT_SMALL,
            bg="#E2E8F0",
            fg=theme.TEXT_SECONDARY
        )
        lbl_status.pack(side="left")

        lbl_version = tk.Label(
            status_frame,
            text="CSE 2nd Year OOP Project",
            font=theme.FONT_SMALL_BOLD,
            bg="#E2E8F0",
            fg=theme.TEXT_SECONDARY
        )
        lbl_version.pack(side="right")

    def switch_to_tab(self, tab_index: int):
        """Programmatic tab navigation helper."""
        self.notebook.select(tab_index)

    def _on_tab_changed(self, event):
        sel_idx = self.notebook.index(self.notebook.select())
        if sel_idx == 0:
            self.view_dashboard.refresh_data()
        elif sel_idx == 1:
            self.view_donors.refresh_data()
        elif sel_idx == 2:
            self.view_inventory.refresh_data()
        elif sel_idx == 3:
            self.view_requests.refresh_data()

    def _initial_load(self):
        self.view_dashboard.refresh_data()
        self.view_donors.refresh_data()
        self.view_inventory.refresh_data()
        self.view_requests.refresh_data()
