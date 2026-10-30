"""
Student Grade Management System - Interactive Console Interface
Provides menu navigation, tabular formatting, input prompts, and error recovery.
"""

import sys
from typing import Optional, Any
from .grade_manager import GradeManager
from .storage import StorageManager
from .validator import InputValidator, ValidationError


class ConsoleUI:
    """Terminal-based user interface for the Student Grade Management System."""

    def __init__(self, data_file: str = "students_data.json"):
        self.manager = GradeManager()
        self.storage = StorageManager(data_file)
        # Attempt automatic loading of existing data
        loaded = self.storage.load_from_file(self.manager)
        if loaded > 0:
            print(f"[Loaded {loaded} student record(s) from {data_file}]")

    def print_header(self, title: str):
        print("\n" + "=" * 65)
        print(f"  {title.upper()}")
        print("=" * 65)

    def print_menu(self):
        print("\n" + "-" * 40)
        print("  STUDENT GRADE MANAGEMENT SYSTEM")
        print("-" * 40)
        print("  [1] Add New Student")
        print("  [2] Enter Student Subject Marks")
        print("  [3] View All Students & Grades")
        print("  [4] View Detailed Student Report Card")
        print("  [5] View Class Performance Analytics")
        print("  [6] View Student Rankings (Leaderboard)")
        print("  [7] Search Student by ID or Name")
        print("  [8] Delete a Student")
        print("  [9] Preload Sample Student Dataset")
        print("  [10] Export Grade Report to CSV")
        print("  [11] Save Data to Disk")
        print("  [0] Exit Application")
        print("-" * 40)

    def prompt_validated_input(self, prompt: str, validator_fn, cancel_val: str = "q") -> Optional[Any]:
        """Loops until valid input is given or user cancels."""
        while True:
            raw = input(f"{prompt} (or '{cancel_val}' to cancel): ").strip()
            if raw.lower() == cancel_val:
                print("-> Operation canceled.")
                return None
            valid, cleaned, err = validator_fn(raw)
            if valid:
                return cleaned
            print(f"  [Error] {err} Please try again.")

    def run_add_student(self):
        self.print_header("Add New Student")
        student_id = self.prompt_validated_input("Enter Student ID (e.g. S101)", InputValidator.validate_student_id)
        if not student_id:
            return

        if self.manager.get_student(student_id):
            print(f"  [Error] Student ID '{student_id}' already exists in registry.")
            return

        name = self.prompt_validated_input("Enter Student Full Name", InputValidator.validate_name)
        if not name:
            return

        try:
            student = self.manager.add_student(student_id, name)
            print(f"\n[Success] Student '{student.name}' (ID: {student.student_id}) enrolled successfully.")
            self.storage.save_to_file(self.manager)

            # Prompt to add marks immediately
            choice = input("Would you like to enter subject marks now? (y/n): ").strip().lower()
            if choice == "y":
                self.run_enter_marks(student.student_id)
        except ValidationError as e:
            print(f"  [Error] {e}")

    def run_enter_marks(self, default_id: Optional[str] = None):
        self.print_header("Enter Student Subject Marks")
        student_id = default_id
        if not student_id:
            student_id = self.prompt_validated_input("Enter Student ID", InputValidator.validate_student_id)
            if not student_id:
                return

        student = self.manager.get_student(student_id)
        if not student:
            print(f"  [Error] Student '{student_id}' not found. Please add the student first.")
            return

        print(f"\nRecording marks for: {student.name} ({student.student_id})")
        print("Type 'done' at the subject prompt when finished entering subjects.")

        while True:
            raw_sub = input("\nEnter Subject Name (or 'done' to finish): ").strip()
            if raw_sub.lower() in ("done", "d", "q"):
                break

            valid_sub, clean_sub, err_sub = InputValidator.validate_subject(raw_sub)
            if not valid_sub:
                print(f"  [Error] {err_sub}")
                continue

            # Prompt mark
            mark_val = None
            while mark_val is None:
                raw_mark = input(f"Enter mark for '{clean_sub}' (0-100): ").strip()
                valid_m, clean_m, err_m = InputValidator.validate_mark(raw_mark)
                if valid_m:
                    mark_val = clean_m
                else:
                    print(f"  [Validation Error] {err_m}")

            score_record = self.manager.add_or_update_mark(student.student_id, clean_sub, mark_val)
            print(f"  -> Recorded: {score_record.subject} = {score_record.mark:.2f} | Grade: {score_record.letter_grade} (GPA {score_record.gpa_point})")

        self.storage.save_to_file(self.manager)
        print(f"\n[Updated] Average Mark: {student.calculate_average():.2f}% | Overall Grade: {student.get_overall_grade()}")

    def run_view_all_students(self):
        self.print_header("All Students Overview")
        students = self.manager.get_all_students()
        if not students:
            print("No student records found in the system.")
            return

        print(f"{'ID':<10} {'Name':<24} {'Subjects':<10} {'Average':<10} {'Grade':<8} {'GPA':<6} {'Status':<6}")
        print("-" * 78)
        for s in students:
            avg = s.calculate_average()
            grade = s.get_overall_grade()
            gpa = s.get_overall_gpa()
            status = "PASS" if s.is_passing() else "FAIL"
            print(f"{s.student_id:<10} {s.name:<24} {len(s.scores):<10} {avg:<10.2f} {grade:<8} {gpa:<6.2f} {status:<6}")
        print("-" * 78)
        print(f"Total Students: {len(students)}")

    def run_view_student_report_card(self):
        self.print_header("Detailed Student Report Card")
        student_id = self.prompt_validated_input("Enter Student ID", InputValidator.validate_student_id)
        if not student_id:
            return

        student = self.manager.get_student(student_id)
        if not student:
            print(f"  [Error] Student '{student_id}' not found.")
            return

        print("\n" + "=" * 60)
        print(f"  OFFICIAL ACADEMIC REPORT CARD")
        print("=" * 60)
        print(f"  Student ID : {student.student_id}")
        print(f"  Full Name  : {student.name}")
        print("-" * 60)
        print(f"{'Subject':<28} {'Mark':<10} {'Grade':<8} {'GPA':<6} {'Result':<8}")
        print("-" * 60)

        if not student.scores:
            print("  [No subject marks recorded yet]")
        else:
            for sub, score in sorted(student.scores.items()):
                res = "PASS" if score.passed else "FAIL"
                print(f"{score.subject:<28} {score.mark:<10.2f} {score.letter_grade:<8} {score.gpa_point:<6.1f} {res:<8}")

        print("-" * 60)
        avg = student.calculate_average()
        grade = student.get_overall_grade()
        gpa = student.get_overall_gpa()
        status = "PASSED" if student.is_passing() else "FAILED"
        print(f"  Cumulative Average : {avg:.2f}%")
        print(f"  Overall Grade      : {grade}")
        print(f"  Cumulative GPA     : {gpa:.2f} / 4.00")
        print(f"  Academic Standing  : {status}")
        print("=" * 60)

    def run_view_analytics(self):
        self.print_header("Class Performance Analytics")
        stats = self.manager.calculate_class_statistics()
        if stats["total_students"] == 0:
            print("No student records available for analytics.")
            return

        print(f"  Total Enrolled Students : {stats['total_students']}")
        print(f"  Overall Class Average   : {stats['class_average']:.2f}%")
        print(f"  Highest Average         : {stats['highest_average']:.2f}% by {stats['highest_student']}")
        print(f"  Lowest Average          : {stats['lowest_average']:.2f}% by {stats['lowest_student']}")
        print(f"  Passing Students        : {stats['pass_count']} ({stats['pass_rate_pct']:.1f}%)")
        print(f"  Failing Students        : {stats['fail_count']} ({100 - stats['pass_rate_pct']:.1f}%)")
        print("\n  Grade Distribution Breakdown:")
        print("  " + "-" * 32)
        dist = stats["grade_distribution"]
        total = stats["total_students"]
        for g in ["A", "B", "C", "D", "F"]:
            cnt = dist.get(g, 0)
            pct = (cnt / total) * 100
            bar = "#" * int(pct // 5)
            print(f"   Grade {g}: {cnt:>2} ({pct:>5.1f}%) | {bar}")
        print("  " + "-" * 32)

    def run_view_rankings(self):
        self.print_header("Student Leaderboard / Academic Rankings")
        ranked = self.manager.get_ranked_students()
        if not ranked:
            print("No students enrolled.")
            return

        print(f"{'Rank':<6} {'ID':<10} {'Name':<24} {'Average':<10} {'Grade':<8} {'GPA':<6}")
        print("-" * 66)
        for rank, s in enumerate(ranked, start=1):
            avg = s.calculate_average()
            grade = s.get_overall_grade()
            gpa = s.get_overall_gpa()
            print(f"{rank:<6} {s.student_id:<10} {s.name:<24} {avg:<10.2f} {grade:<8} {gpa:<6.2f}")
        print("-" * 66)

    def run_search(self):
        self.print_header("Search Student Registry")
        kw = input("Enter search term (Student ID or Name): ").strip()
        if not kw:
            print("Search canceled.")
            return

        results = self.manager.search_students(kw)
        if not results:
            print(f"No students matching '{kw}' found.")
            return

        print(f"\nFound {len(results)} matching record(s):")
        print(f"{'ID':<10} {'Name':<24} {'Average':<10} {'Grade':<8} {'Status':<6}")
        print("-" * 62)
        for s in results:
            avg = s.calculate_average()
            grade = s.get_overall_grade()
            status = "PASS" if s.is_passing() else "FAIL"
            print(f"{s.student_id:<10} {s.name:<24} {avg:<10.2f} {grade:<8} {status:<6}")
        print("-" * 62)

    def run_delete_student(self):
        self.print_header("Delete Student Record")
        sid = input("Enter Student ID to delete: ").strip()
        student = self.manager.get_student(sid)
        if not student:
            print(f"  [Error] Student '{sid}' not found.")
            return

        confirm = input(f"Are you sure you want to delete {student.name} ({student.student_id})? (y/n): ").strip().lower()
        if confirm == "y":
            self.manager.remove_student(sid)
            self.storage.save_to_file(self.manager)
            print(f"[Deleted] Student '{sid}' removed.")
        else:
            print("Deletion canceled.")

    def run_seed_sample_data(self):
        self.print_header("Preload Sample Data")
        count = self.storage.seed_sample_data(self.manager)
        self.storage.save_to_file(self.manager)
        print(f"[Done] Loaded {count} new sample students with realistic grades.")

    def run_export_csv(self):
        self.print_header("Export Grade Report to CSV")
        filename = input("Enter output CSV filename (default: grade_report.csv): ").strip()
        if not filename:
            filename = "grade_report.csv"
        success = self.storage.export_summary_csv(self.manager, filename)
        if success:
            print(f"[Success] Grade report successfully exported to '{filename}'.")

    def run(self):
        """Main interaction loop."""
        while True:
            self.print_menu()
            choice = input("Enter option (0-11): ").strip()

            if choice == "1":
                self.run_add_student()
            elif choice == "2":
                self.run_enter_marks()
            elif choice == "3":
                self.run_view_all_students()
            elif choice == "4":
                self.run_view_student_report_card()
            elif choice == "5":
                self.run_view_analytics()
            elif choice == "6":
                self.run_view_rankings()
            elif choice == "7":
                self.run_search()
            elif choice == "8":
                self.run_delete_student()
            elif choice == "9":
                self.run_seed_sample_data()
            elif choice == "10":
                self.run_export_csv()
            elif choice == "11":
                self.storage.save_to_file(self.manager)
                print("[Saved] Records successfully written to disk.")
            elif choice == "0":
                self.storage.save_to_file(self.manager)
                print("\nThank you for using the Student Grade Management System. Goodbye!\n")
                break
            else:
                print("  [Error] Invalid selection. Please enter a number between 0 and 11.")


if __name__ == "__main__":
    app = ConsoleUI()
    app.run()
