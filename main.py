"""
main.py
Main entry point for Blood Donation Management System.
Run this file to launch the GUI application.
"""
import sys
import os

# Ensure package roots are on Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.app import BloodDonationApp


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data")

    print("=" * 60)
    print(" Blood Donation Management System (BDMS)")
    print(" 2nd Year OOP Project - Python & Tkinter")
    print(f" Data Folder: {data_dir}")
    print("=" * 60)

    try:
        app = BloodDonationApp(data_directory=data_dir)
        app.mainloop()
    except KeyboardInterrupt:
        print("\nExiting program.")
    except Exception as e:
        print(f"\nError: {e}")
        raise e


if __name__ == "__main__":
    main()
