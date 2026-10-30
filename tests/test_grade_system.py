"""
Unit and Integration Test Suite for Student Grade Management System.
Covers Input Validation, Boundary Value Analysis, Grade Calculations, and Storage.
"""

import unittest
import os
import tempfile
import json
from grade_system.models import Student, SubjectScore, mark_to_letter_grade, letter_to_gpa
from grade_system.validator import InputValidator, ValidationError
from grade_system.grade_manager import GradeManager
from grade_system.storage import StorageManager


class TestValidation(unittest.TestCase):
    """Test suite for InputValidator."""

    def test_student_id_valid(self):
        valid_ids = ["S101", "STU-001", "CS_2026", "A1"]
        for sid in valid_ids:
            is_valid, cleaned, err = InputValidator.validate_student_id(sid)
            self.assertTrue(is_valid, f"Failed for valid ID: {sid}")
            self.assertIsNone(err)
            self.assertEqual(cleaned, sid.upper())

    def test_student_id_invalid(self):
        invalid_ids = ["", "   ", "A", "S@101", "ID With Space", "Toolongstudentidentifierexceedinglimit"]
        for sid in invalid_ids:
            is_valid, cleaned, err = InputValidator.validate_student_id(sid)
            self.assertFalse(is_valid, f"Expected invalid for: {sid}")
            self.assertIsNotNone(err)

    def test_student_name_valid(self):
        valid_names = ["John Doe", "Mary-Jane", "O'Connor", "Dr. Alan Turing"]
        for name in valid_names:
            is_valid, cleaned, err = InputValidator.validate_name(name)
            self.assertTrue(is_valid, f"Failed for valid name: {name}")
            self.assertIsNone(err)

    def test_student_name_invalid(self):
        invalid_names = ["", "   ", "X", "12345", "John@Doe", "Test#Name"]
        for name in invalid_names:
            is_valid, cleaned, err = InputValidator.validate_name(name)
            self.assertFalse(is_valid, f"Expected invalid for name: {name}")
            self.assertIsNotNone(err)

    def test_mark_valid_boundaries(self):
        test_cases = [
            (0, 0.0),
            (0.0, 0.0),
            (50.5, 50.5),
            (60, 60.0),
            (85.75, 85.75),
            (100, 100.0),
            (100.0, 100.0),
            ("88.5", 88.5),
            ("100", 100.0),
        ]
        for raw, expected in test_cases:
            is_valid, val, err = InputValidator.validate_mark(raw)
            self.assertTrue(is_valid, f"Failed for mark: {raw}")
            self.assertEqual(val, expected)
            self.assertIsNone(err)

    def test_mark_invalid_boundaries_and_types(self):
        invalid_marks = [-0.1, -50, 100.1, 150, "abc", "one hundred", "", None]
        for raw in invalid_marks:
            is_valid, val, err = InputValidator.validate_mark(raw)
            self.assertFalse(is_valid, f"Expected invalid for mark: {raw}")
            self.assertIsNotNone(err)


class TestGradingLogic(unittest.TestCase):
    """Test suite for letter grade assignment and GPA mapping."""

    def test_letter_grade_boundary_partitions(self):
        # Grade A: 90 - 100
        self.assertEqual(mark_to_letter_grade(100.0), "A")
        self.assertEqual(mark_to_letter_grade(95.0), "A")
        self.assertEqual(mark_to_letter_grade(90.0), "A")

        # Grade B: 80 - 89.99
        self.assertEqual(mark_to_letter_grade(89.99), "B")
        self.assertEqual(mark_to_letter_grade(85.0), "B")
        self.assertEqual(mark_to_letter_grade(80.0), "B")

        # Grade C: 70 - 79.99
        self.assertEqual(mark_to_letter_grade(79.99), "C")
        self.assertEqual(mark_to_letter_grade(75.0), "C")
        self.assertEqual(mark_to_letter_grade(70.0), "C")

        # Grade D: 60 - 69.99
        self.assertEqual(mark_to_letter_grade(69.99), "D")
        self.assertEqual(mark_to_letter_grade(65.0), "D")
        self.assertEqual(mark_to_letter_grade(60.0), "D")

        # Grade F: 0 - 59.99
        self.assertEqual(mark_to_letter_grade(59.99), "F")
        self.assertEqual(mark_to_letter_grade(45.0), "F")
        self.assertEqual(mark_to_letter_grade(0.0), "F")

    def test_gpa_mapping(self):
        self.assertEqual(letter_to_gpa("A"), 4.0)
        self.assertEqual(letter_to_gpa("B"), 3.0)
        self.assertEqual(letter_to_gpa("C"), 2.0)
        self.assertEqual(letter_to_gpa("D"), 1.0)
        self.assertEqual(letter_to_gpa("F"), 0.0)


class TestStudentModel(unittest.TestCase):
    """Test suite for Student class methods and calculations."""

    def setUp(self):
        self.student = Student(student_id="S101", name="Alice Cooper")

    def test_student_empty_scores(self):
        self.assertEqual(self.student.calculate_average(), 0.0)
        self.assertEqual(self.student.get_overall_grade(), "F")
        self.assertEqual(self.student.get_overall_gpa(), 0.0)
        self.assertFalse(self.student.is_passing())

    def test_student_average_calculation(self):
        self.student.add_score("Math", 90.0)
        self.student.add_score("Physics", 80.0)
        self.student.add_score("English", 70.0)

        # Average = (90 + 80 + 70) / 3 = 80.0
        self.assertEqual(self.student.calculate_average(), 80.0)
        self.assertEqual(self.student.get_overall_grade(), "B")
        # GPA = (4.0 + 3.0 + 2.0) / 3 = 3.0
        self.assertEqual(self.student.get_overall_gpa(), 3.0)
        self.assertTrue(self.student.is_passing())

    def test_update_and_remove_score(self):
        self.student.add_score("Math", 70.0)
        self.assertEqual(self.student.scores["Math"].mark, 70.0)

        # Update mark
        self.student.add_score("Math", 95.0)
        self.assertEqual(self.student.scores["Math"].mark, 95.0)
        self.assertEqual(self.student.scores["Math"].letter_grade, "A")

        # Remove mark
        removed = self.student.remove_score("Math")
        self.assertTrue(removed)
        self.assertNotIn("Math", self.student.scores)


class TestGradeManager(unittest.TestCase):
    """Test suite for GradeManager business logic."""

    def setUp(self):
        self.manager = GradeManager()

    def test_add_duplicate_student_raises_error(self):
        self.manager.add_student("S101", "Emma Watson")
        with self.assertRaises(ValidationError):
            self.manager.add_student("S101", "Emma Watson Duplicate")

    def test_add_mark_for_nonexistent_student_raises_error(self):
        with self.assertRaises(ValidationError):
            self.manager.add_or_update_mark("UNKNOWN", "Math", 85)

    def test_class_statistics(self):
        s1 = self.manager.add_student("S101", "Alice")
        s1.add_score("Math", 95.0)

        s2 = self.manager.add_student("S102", "Bob")
        s2.add_score("Math", 85.0)

        s3 = self.manager.add_student("S103", "Charlie")
        s3.add_score("Math", 50.0)

        stats = self.manager.calculate_class_statistics()
        self.assertEqual(stats["total_students"], 3)
        # Average: (95 + 85 + 50) / 3 = 76.67
        self.assertEqual(stats["class_average"], 76.67)
        self.assertEqual(stats["pass_count"], 2)
        self.assertEqual(stats["fail_count"], 1)
        self.assertEqual(stats["grade_distribution"]["A"], 1)
        self.assertEqual(stats["grade_distribution"]["B"], 1)
        self.assertEqual(stats["grade_distribution"]["F"], 1)
        self.assertIn("Alice", stats["highest_student"])
        self.assertIn("Charlie", stats["lowest_student"])

    def test_search_and_rankings(self):
        self.manager.add_student("S101", "Alice Smith")
        self.manager.add_or_update_mark("S101", "Math", 70)

        self.manager.add_student("S102", "Bob Jones")
        self.manager.add_or_update_mark("S102", "Math", 95)

        # Search
        results = self.manager.search_students("bob")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].student_id, "S102")

        # Rankings
        ranked = self.manager.get_ranked_students()
        self.assertEqual(ranked[0].student_id, "S102")  # Bob has 95
        self.assertEqual(ranked[1].student_id, "S101")  # Alice has 70


class TestStorage(unittest.TestCase):
    """Test suite for StorageManager file persistence and CSV exports."""

    def test_json_save_and_load(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tf:
            temp_path = tf.name

        try:
            storage = StorageManager(temp_path)
            mgr1 = GradeManager()
            mgr1.add_student("S101", "David Miller")
            mgr1.add_or_update_mark("S101", "Physics", 88.0)

            saved = storage.save_to_file(mgr1)
            self.assertTrue(saved)

            mgr2 = GradeManager()
            loaded = storage.load_from_file(mgr2)
            self.assertEqual(loaded, 1)

            st = mgr2.get_student("S101")
            self.assertIsNotNone(st)
            self.assertEqual(st.name, "David Miller")
            self.assertEqual(st.scores["Physics"].mark, 88.0)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


if __name__ == "__main__":
    unittest.main()

