"""
ui/theme.py
Defines the visual design system, colors, and styling rules.
Provides a modern, clean, clinical user interface.
"""
import tkinter as tk
from tkinter import ttk

# Palette
PRIMARY_COLOR = "#B71C1C"       # Hospital Red
PRIMARY_LIGHT = "#EF4444"       # Urgent Crimson
PRIMARY_DARK = "#7F1D1D"        # Deep Burgundy
SECONDARY_COLOR = "#0F172A"     # Midnight Navy
BG_MAIN = "#F1F5F9"             # Soft Clean Canvas
BG_CARD = "#FFFFFF"             # Crisp White Card
BORDER_COLOR = "#CBD5E1"        # Subtle Border
TEXT_PRIMARY = "#0F172A"        # Deep Slate
TEXT_SECONDARY = "#475569"      # Cool Grey
TEXT_MUTED = "#94A3B8"          # Pale Grey

SUCCESS_COLOR = "#10B981"       # Mint Green
WARNING_COLOR = "#F59E0B"       # Warning Amber
DANGER_COLOR = "#DC2626"        # Alert Red
INFO_COLOR = "#0284C7"          # Medical Blue

FONT_FAMILY = "Segoe UI" if tk.TkVersion >= 8.6 else "Helvetica"
FONT_TITLE = (FONT_FAMILY, 16, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")
FONT_HEADING = (FONT_FAMILY, 11, "bold")
FONT_BODY = (FONT_FAMILY, 10, "normal")
FONT_BODY_BOLD = (FONT_FAMILY, 10, "bold")
FONT_SMALL = (FONT_FAMILY, 9, "normal")
FONT_SMALL_BOLD = (FONT_FAMILY, 9, "bold")
FONT_STAT_VAL = (FONT_FAMILY, 20, "bold")


def configure_app_styles(root: tk.Tk):
    """Configures global ttk style overrides for unified appearance."""
    style = ttk.Style(root)
    
    # Try clam theme as standard base for customizable widgets
    available_themes = style.theme_names()
    if "clam" in available_themes:
        style.theme_use("clam")

    # Notebook Tabs
    style.configure("TNotebook", background=BG_MAIN, borderwidth=0)
    style.configure(
        "TNotebook.Tab",
        font=FONT_BODY_BOLD,
        padding=[14, 8],
        background="#E2E8F0",
        foreground=TEXT_SECONDARY,
        borderwidth=0
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", PRIMARY_COLOR)],
        foreground=[("selected", "#FFFFFF")]
    )

    # Treeview (Tables)
    style.configure(
        "Treeview",
        background="#FFFFFF",
        foreground=TEXT_PRIMARY,
        rowheight=26,
        fieldbackground="#FFFFFF",
        font=FONT_BODY,
        borderwidth=1
    )
    style.configure(
        "Treeview.Heading",
        background="#E2E8F0",
        foreground=TEXT_PRIMARY,
        font=FONT_HEADING,
        relief="flat",
        padding=[6, 6]
    )
    style.map("Treeview", background=[("selected", "#E0E7FF")], foreground=[("selected", PRIMARY_DARK)])

    # Buttons
    style.configure(
        "Primary.TButton",
        font=FONT_BODY_BOLD,
        background=PRIMARY_COLOR,
        foreground="#FFFFFF",
        padding=[12, 6],
        borderwidth=0
    )
    style.map(
        "Primary.TButton",
        background=[("active", PRIMARY_DARK), ("disabled", "#CBD5E1")],
        foreground=[("disabled", "#94A3B8")]
    )

    style.configure(
        "Success.TButton",
        font=FONT_BODY_BOLD,
        background=SUCCESS_COLOR,
        foreground="#FFFFFF",
        padding=[12, 6],
        borderwidth=0
    )
    style.map("Success.TButton", background=[("active", "#059669")])

    style.configure(
        "Secondary.TButton",
        font=FONT_BODY,
        background="#E2E8F0",
        foreground=TEXT_PRIMARY,
        padding=[10, 5],
        borderwidth=0
    )
    style.map("Secondary.TButton", background=[("active", "#CBD5E1")])
