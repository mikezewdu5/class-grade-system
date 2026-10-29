"""
Student Grade Management System - Domain Models
Defines Student, SubjectScore, and grading criteria.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


def mark_to_letter_grade(mark: float) -> str:
    """
    Converts a numerical mark (0-100) to a letter grade:
    - 90 - 100: A (Excellent)
    - 80 - 89.99: B (Good)
    - 70 - 79.99: C (Satisfactory)
    - 60 - 69.99: D (Sufficient)
    - 0 - 59.99: F (Fail)
    """
    if mark >= 90.0:
        return "A"
    elif mark >= 80.0:
        return "B"
    elif mark >= 70.0:
        return "C"
    elif mark >= 60.0:
        return "D"
    else:
        return "F"


def letter_to_gpa(letter: str) -> float:
    """Maps letter grade to standard 4.0 scale GPA."""
    mapping = {
        "A": 4.0,
        "B": 3.0,
        "C": 2.0,
        "D": 1.0,
        "F": 0.0
    }
    return mapping.get(letter.upper(), 0.0)


@dataclass
class SubjectScore:
    subject: str
    mark: float
    letter_grade: str = field(init=False)
    gpa_point: float = field(init=False)
    passed: bool = field(init=False)

    def __post_init__(self):
        self.mark = round(float(self.mark), 2)
        self.letter_grade = mark_to_letter_grade(self.mark)
        self.gpa_point = letter_to_gpa(self.letter_grade)
        self.passed = self.mark >= 60.0

    def to_dict(self) -> dict:
        return {
            "subject": self.subject,
            "mark": self.mark,
            "letter_grade": self.letter_grade,
            "gpa_point": self.gpa_point,
            "passed": self.passed
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SubjectScore":
        return cls(subject=data["subject"], mark=data["mark"])


class Student:
    """Represents a student enrolled with academic subject records."""

    def __init__(self, student_id: str, name: str, scores: Optional[Dict[str, SubjectScore]] = None):
        self.student_id = student_id.strip()
        self.name = name.strip()
        self.scores: Dict[str, SubjectScore] = scores or {}

    def add_score(self, subject: str, mark: float) -> SubjectScore:
        score = SubjectScore(subject=subject.strip(), mark=mark)
        self.scores[subject.strip()] = score
        return score

    def remove_score(self, subject: str) -> bool:
        if subject in self.scores:
            del self.scores[subject]
            return True
        return False

    def calculate_average(self) -> float:
        if not self.scores:
            return 0.0
        total = sum(s.mark for s in self.scores.values())
        return round(total / len(self.scores), 2)

    def get_overall_grade(self) -> str:
        avg = self.calculate_average()
        return mark_to_letter_grade(avg)

    def get_overall_gpa(self) -> float:
        if not self.scores:
            return 0.0
        total_gpa = sum(s.gpa_point for s in self.scores.values())
        return round(total_gpa / len(self.scores), 2)

    def is_passing(self) -> bool:
        """A student passes overall if average mark >= 60.0 and no failing subjects."""
        if not self.scores:
            return False
        return self.calculate_average() >= 60.0

    def to_dict(self) -> dict:
        return {
            "student_id": self.student_id,
            "name": self.name,
            "scores": {subj: score.to_dict() for subj, score in self.scores.items()}
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Student":
        student = cls(student_id=data["student_id"], name=data["name"])
        for subj, score_data in data.get("scores", {}).items():
            student.add_score(score_data["subject"], score_data["mark"])
        return student

