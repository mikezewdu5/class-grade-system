"""
Student Grade Management System - Business Logic Manager
Orchestrates student registry, mark records, calculations, and analytics.
"""

from typing import Dict, List, Optional, Any
from .models import Student, SubjectScore, mark_to_letter_grade
from .validator import InputValidator, ValidationError


class GradeManager:
    """Manages collection of students, grade recording, and statistical summaries."""

    def __init__(self):
        self._students: Dict[str, Student] = {}

    def add_student(self, student_id: str, name: str) -> Student:
        """Adds a new student after validation."""
        valid_id, clean_id, err_id = InputValidator.validate_student_id(student_id)
        if not valid_id:
            raise ValidationError(err_id)

        valid_name, clean_name, err_name = InputValidator.validate_name(name)
        if not valid_name:
            raise ValidationError(err_name)

        if clean_id in self._students:
            raise ValidationError(f"Student with ID '{clean_id}' already exists.")

        student = Student(student_id=clean_id, name=clean_name)
        self._students[clean_id] = student
        return student

    def get_student(self, student_id: str) -> Optional[Student]:
        """Retrieves a student by ID."""
        if not student_id:
            return None
        return self._students.get(student_id.strip().upper())

    def remove_student(self, student_id: str) -> bool:
        """Removes a student by ID."""
        clean_id = student_id.strip().upper() if student_id else ""
        if clean_id in self._students:
            del self._students[clean_id]
            return True
        return False

    def add_or_update_mark(self, student_id: str, subject: str, mark: Any) -> SubjectScore:
        """Validates and records a mark for a student in a specific subject."""
        student = self.get_student(student_id)
        if not student:
            raise ValidationError(f"Student with ID '{student_id}' does not exist.")

        valid_sub, clean_sub, err_sub = InputValidator.validate_subject(subject)
        if not valid_sub:
            raise ValidationError(err_sub)

        valid_mark, clean_mark, err_mark = InputValidator.validate_mark(mark)
        if not valid_mark:
            raise ValidationError(err_mark)

        return student.add_score(clean_sub, clean_mark)

    def get_all_students(self) -> List[Student]:
        """Returns all students sorted alphabetically by ID."""
        return sorted(self._students.values(), key=lambda s: s.student_id)

    def search_students(self, keyword: str) -> List[Student]:
        """Searches students by substring in ID or name."""
        kw = keyword.strip().lower()
        if not kw:
            return self.get_all_students()
        return [
            s for s in self._students.values()
            if kw in s.student_id.lower() or kw in s.name.lower()
        ]

    def get_ranked_students(self) -> List[Student]:
        """Returns students ordered by overall average descending."""
        return sorted(self._students.values(), key=lambda s: s.calculate_average(), reverse=True)

    def calculate_class_statistics(self) -> Dict[str, Any]:
        """Computes comprehensive class-wide performance metrics."""
        students = list(self._students.values())
        total_students = len(students)

        if total_students == 0:
            return {
                "total_students": 0,
                "class_average": 0.0,
                "grade_distribution": {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0},
                "highest_student": None,
                "highest_average": 0.0,
                "lowest_student": None,
                "lowest_average": 0.0,
                "pass_count": 0,
                "fail_count": 0,
                "pass_rate_pct": 0.0
            }

        averages = [(s, s.calculate_average()) for s in students]
        class_avg = round(sum(avg for _, avg in averages) / total_students, 2)

        distribution = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        pass_count = 0

        for s, avg in averages:
            grade = s.get_overall_grade()
            distribution[grade] = distribution.get(grade, 0) + 1
            if avg >= 60.0:
                pass_count += 1

        fail_count = total_students - pass_count
        pass_rate = round((pass_count / total_students) * 100, 2)

        # Sort by average
        sorted_by_avg = sorted(averages, key=lambda x: x[1])
        lowest_student, lowest_avg = sorted_by_avg[0]
        highest_student, highest_avg = sorted_by_avg[-1]

        return {
            "total_students": total_students,
            "class_average": class_avg,
            "grade_distribution": distribution,
            "highest_student": f"{highest_student.name} ({highest_student.student_id})",
            "highest_average": highest_avg,
            "lowest_student": f"{lowest_student.name} ({lowest_student.student_id})",
            "lowest_average": lowest_avg,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate_pct": pass_rate
        }

    def clear(self):
        """Clears all records."""
        self._students.clear()

