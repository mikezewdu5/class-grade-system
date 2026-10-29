"""
Student Grade Management System - Input Validator
Provides validation logic with clear error messages.
"""

import re
from typing import Tuple, Optional, Any


class ValidationError(ValueError):
    """Custom exception raised when user input fails validation."""
    pass


class InputValidator:
    """Validates inputs for student profiles, subject names, and academic marks."""

    @staticmethod
    def validate_student_id(student_id: Any) -> Tuple[bool, str, Optional[str]]:
        """
        Validates a student ID.
        Rule: 2-20 characters, alphanumeric, dashes or underscores allowed.
        Returns: (is_valid, cleaned_id_or_empty, error_message)
        """
        if student_id is None:
            return False, "", "Student ID cannot be empty."
        
        cleaned = str(student_id).strip()
        if not cleaned:
            return False, "", "Student ID cannot be blank."
        
        if len(cleaned) < 2 or len(cleaned) > 20:
            return False, "", "Student ID must be between 2 and 20 characters."
        
        if not re.match(r"^[A-Za-z0-9\-_]+$", cleaned):
            return False, "", "Student ID can only contain letters, numbers, hyphens, or underscores."
        
        return True, cleaned.upper(), None

    @staticmethod
    def validate_name(name: Any) -> Tuple[bool, str, Optional[str]]:
        """
        Validates student name.
        Rule: 2-60 characters, letters, spaces, hyphens, and apostrophes.
        """
        if name is None:
            return False, "", "Student name cannot be empty."
        
        cleaned = str(name).strip()
        if not cleaned:
            return False, "", "Student name cannot be blank."
        
        if len(cleaned) < 2 or len(cleaned) > 60:
            return False, "", "Student name must be between 2 and 60 characters."
        
        if not re.match(r"^[A-Za-z\s\-'.]+$", cleaned):
            return False, "", "Student name can only contain alphabetic characters, spaces, hyphens, apostrophes, and periods."
        
        return True, cleaned.title(), None

    @staticmethod
    def validate_subject(subject: Any) -> Tuple[bool, str, Optional[str]]:
        """
        Validates course/subject name.
        Rule: 2-50 characters, letters, numbers, spaces, and hyphens.
        """
        if subject is None:
            return False, "", "Subject name cannot be empty."
        
        cleaned = str(subject).strip()
        if not cleaned:
            return False, "", "Subject name cannot be blank."
        
        if len(cleaned) < 2 or len(cleaned) > 50:
            return False, "", "Subject name must be between 2 and 50 characters."
        
        if not re.match(r"^[A-Za-z0-9\s\-_&.]+$", cleaned):
            return False, "", "Subject name contains invalid characters."
        
        return True, cleaned.title(), None

    @staticmethod
    def validate_mark(mark: Any) -> Tuple[bool, float, Optional[str]]:
        """
        Validates an academic mark.
        Rules:
        - Must be numeric (integer or floating point)
        - Must be within [0.0, 100.0]
        Returns: (is_valid, float_mark, error_message)
        """
        if mark is None or (isinstance(mark, str) and mark.strip() == ""):
            return False, 0.0, "Mark cannot be empty. Please enter a number between 0 and 100."
        
        try:
            val = float(mark)
        except (ValueError, TypeError):
            return False, 0.0, f"Invalid mark '{mark}'. Mark must be a numeric value."
        
        if val < 0.0:
            return False, val, f"Mark {val:.2f} cannot be negative. Must be between 0 and 100."
        
        if val > 100.0:
            return False, val, f"Mark {val:.2f} exceeds maximum score. Must be between 0 and 100."
        
        return True, round(val, 2), None

