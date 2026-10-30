"""
Student Grade Management System - Storage & Persistence
Handles JSON serialization, persistence, sample data seeding, and CSV exports.
"""

import json
import os
import csv
from typing import List
from .models import Student
from .grade_manager import GradeManager


class StorageManager:
    """Manages saving and loading grade records to disk."""

    def __init__(self, data_file: str = "students_data.json"):
        self.data_file = data_file

    def save_to_file(self, manager: GradeManager) -> bool:
        """Saves all students and their marks to JSON file."""
        data = [s.to_dict() for s in manager.get_all_students()]
        try:
            os.makedirs(os.path.dirname(os.path.abspath(self.data_file)), exist_ok=True)
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            return True
        except IOError as e:
            print(f"[Error saving data: {e}]")
            return False

    def load_from_file(self, manager: GradeManager) -> int:
        """Loads students from JSON file into the manager. Returns count loaded."""
        if not os.path.exists(self.data_file):
            return 0
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded_count = 0
            for item in data:
                student = Student.from_dict(item)
                manager._students[student.student_id] = student
                loaded_count += 1
            return loaded_count
        except (IOError, json.JSONDecodeError) as e:
            print(f"[Error loading data: {e}]")
            return 0

    def seed_sample_data(self, manager: GradeManager) -> int:
        """Seeds realistic sample student data across various performance levels."""
        samples = [
            ("S101", "Emma Watson", {"Mathematics": 94.5, "Physics": 91.0, "Chemistry": 89.0, "English": 96.0}),
            ("S102", "Liam Smith", {"Mathematics": 82.0, "Physics": 78.5, "Chemistry": 85.0, "English": 88.0}),
            ("S103", "Sophia Chen", {"Mathematics": 74.0, "Physics": 71.5, "Chemistry": 69.0, "English": 76.0}),
            ("S104", "Noah Patel", {"Mathematics": 63.5, "Physics": 59.0, "Chemistry": 61.0, "English": 67.0}),
            ("S105", "Olivia Taylor", {"Mathematics": 52.0, "Physics": 48.0, "Chemistry": 55.5, "English": 58.0}),
            ("S106", "Alexander Davis", {"Mathematics": 88.0, "Physics": 84.0, "Chemistry": 90.5, "English": 82.0}),
        ]
        count = 0
        for sid, name, marks in samples:
            if sid not in manager._students:
                s = manager.add_student(sid, name)
                for sub, mk in marks.items():
                    manager.add_or_update_mark(sid, sub, mk)
                count += 1
        return count

    def export_summary_csv(self, manager: GradeManager, csv_path: str = "grade_report.csv") -> bool:
        """Exports a tabular summary of students, average marks, and letter grades to CSV."""
        try:
            with open(csv_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Rank", "Student ID", "Name", "Total Subjects", "Average Mark", "Letter Grade", "GPA", "Status"])
                ranked = manager.get_ranked_students()
                for rank, s in enumerate(ranked, start=1):
                    avg = s.calculate_average()
                    grade = s.get_overall_grade()
                    gpa = s.get_overall_gpa()
                    status = "PASS" if s.is_passing() else "FAIL"
                    writer.writerow([rank, s.student_id, s.name, len(s.scores), f"{avg:.2f}", grade, f"{gpa:.2f}", status])
            return True
        except IOError as e:
            print(f"[Error exporting CSV: {e}]")
            return False

