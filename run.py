"""
Entry point for running the Student Grade Management System (SGMS).
Supports both Interactive Terminal CLI and Desktop Graphical GUI.
"""

import sys
import argparse
from grade_system.cli import ConsoleUI
from grade_system.gui import launch_gui


def main():
    parser = argparse.ArgumentParser(description="Student Grade Management System (SGMS)")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the desktop Graphical User Interface (Tkinter)"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Launch the interactive terminal Console User Interface (Default)"
    )
    args = parser.parse_args()

    if args.gui:
        print("[Launching Student Grade Management System GUI Window...]")
        launch_gui()
    else:
        app = ConsoleUI("students_data.json")
        app.run()


if __name__ == "__main__":
    main()
