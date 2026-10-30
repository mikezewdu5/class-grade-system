"""
Automated Demonstration Script for Student Grade Management System (SGMS).
Runs an end-to-end walkthrough verifying all functional requirements:
- Enrollment
- Input validation (boundary and type violations)
- Mark calculations (averages, letter grades, GPAs)
- Class statistics & rankings
- Persistence & PDF compilation
"""

import sys
from grade_system.models import Student, mark_to_letter_grade, letter_to_gpa
from grade_system.validator import InputValidator, ValidationError
from grade_system.grade_manager import GradeManager
from grade_system.storage import StorageManager
import generate_report_pdf


def print_banner(msg: str):
    print("\n" + "=" * 70)
    print(f"  {msg}")
    print("=" * 70)


def run_demo():
    print_banner("1. DEMONSTRATING INPUT VALIDATION ENGINE")
    
    # Validation tests
    test_inputs = [
        ("Student ID", "S101", InputValidator.validate_student_id),
        ("Student ID (Invalid symbols)", "S@101#", InputValidator.validate_student_id),
        ("Student Name", "Ada Lovelace", InputValidator.validate_name),
        ("Student Name (Numbers)", "12345", InputValidator.validate_name),
        ("Mark (Valid)", "88.50", InputValidator.validate_mark),
        ("Mark (Boundary Upper)", "100.00", InputValidator.validate_mark),
        ("Mark (Negative Error)", "-15.00", InputValidator.validate_mark),
        ("Mark (Overflow Error)", "105.00", InputValidator.validate_mark),
        ("Mark (Text Error)", "Ninety-Five", InputValidator.validate_mark),
    ]
    
    for label, val, fn in test_inputs:
        valid, clean, err = fn(val)
        status = "[VALID]" if valid else "[REJECTED]"
        details = f"Cleaned: '{clean}'" if valid else f"Error: '{err}'"
        print(f"  {status:<11} {label:<28} Input: {str(val):<14} -> {details}")

    print_banner("2. ENROLLING STUDENTS & RECORDING ACADEMIC MARKS")
    manager = GradeManager()
    storage = StorageManager("students_data.json")

    # Add students
    cohort = [
        ("S101", "Emma Watson", {"Mathematics": 94.5, "Physics": 91.0, "Chemistry": 89.0, "English": 96.0}),
        ("S102", "Liam Smith", {"Mathematics": 82.0, "Physics": 78.5, "Chemistry": 85.0, "English": 88.0}),
        ("S103", "Sophia Chen", {"Mathematics": 74.0, "Physics": 71.5, "Chemistry": 69.0, "English": 76.0}),
        ("S104", "Noah Patel", {"Mathematics": 63.5, "Physics": 59.0, "Chemistry": 61.0, "English": 67.0}),
        ("S105", "Olivia Taylor", {"Mathematics": 52.0, "Physics": 48.0, "Chemistry": 55.5, "English": 58.0}),
        ("S106", "Alexander Davis", {"Mathematics": 88.0, "Physics": 84.0, "Chemistry": 90.5, "English": 82.0}),
    ]

    for sid, name, scores in cohort:
        st = manager.add_student(sid, name)
        for sub, mk in scores.items():
            manager.add_or_update_mark(sid, sub, mk)
        print(f"  [Enrolled] {st.name:<18} (ID: {st.student_id}) with {len(st.scores)} subjects recorded.")

    print_banner("3. ACADEMIC LEADERBOARD / RANKINGS")
    ranked = manager.get_ranked_students()
    print(f"  {'Rank':<6} {'ID':<8} {'Name':<20} {'Average':<10} {'Grade':<8} {'GPA':<6} {'Status':<6}")
    print("  " + "-" * 66)
    for rank, s in enumerate(ranked, start=1):
        avg = s.calculate_average()
        grade = s.get_overall_grade()
        gpa = s.get_overall_gpa()
        status = "PASS" if s.is_passing() else "FAIL"
        print(f"  {rank:<6} {s.student_id:<8} {s.name:<20} {avg:<10.2f} {grade:<8} {gpa:<6.2f} {status:<6}")

    print_banner("4. CLASS-WIDE PERFORMANCE ANALYTICS")
    stats = manager.calculate_class_statistics()
    print(f"  Total Enrolled Students : {stats['total_students']}")
    print(f"  Overall Class Average   : {stats['class_average']:.2f}%")
    print(f"  Highest Average         : {stats['highest_average']:.2f}% ({stats['highest_student']})")
    print(f"  Lowest Average          : {stats['lowest_average']:.2f}% ({stats['lowest_student']})")
    print(f"  Passing Rate            : {stats['pass_rate_pct']:.1f}% ({stats['pass_count']} Pass, {stats['fail_count']} Fail)")
    print("  Grade Distribution:")
    for g, cnt in stats["grade_distribution"].items():
        bar = "#" * cnt
        print(f"    Grade {g}: {cnt} student(s) | {bar}")

    print_banner("5. PERSISTING RECORDS & COMPILING PDF REPORT")
    storage.save_to_file(manager)
    print("  [Saved] Student records saved to 'students_data.json'.")
    storage.export_summary_csv(manager, "grade_report.csv")
    print("  [Exported] Grade summary saved to 'grade_report.csv'.")
    generate_report_pdf.build_pdf_report("Student_Grade_Management_System_Project_Report.pdf")
    print("  [Compiled] Publication-quality report 'Student_Grade_Management_System_Project_Report.pdf' ready.")

    print_banner("ALL FUNCTIONAL REQUIREMENTS SUCCESSFULLY DEMONSTRATED")


if __name__ == "__main__":
    run_demo()

