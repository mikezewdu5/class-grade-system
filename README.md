# Student Grade Management System (SGMS)

A robust, simple Student Grade Management System in Python that accepts student marks, validates inputs with strict boundary checking, calculates average marks and standard letter grades, and presents formatted academic results and class statistics.

---

## Features

- **Student Profile Management:** Add, search, list, and delete student records with unique ID enforcement.
- **Strict Input Validation:**
  - Range validation: $0.00 \le \text{mark} \le 100.00$.
  - Rejection of non-numeric inputs, negative marks, and marks exceeding 100.
  - Alphanumeric ID and alphabetic name validation.
  - Graceful cancellation (`q`) available at any prompt.
- **Academic Calculations:**
  - Per-subject letter grade and 4.0 GPA points.
  - Cumulative student average marks (rounded to 2 decimal places).
  - Overall student letter grades (A: 90-100, B: 80-89, C: 70-79, D: 60-69, F: 0-59).
  - Cumulative 4.0 GPA.
  - Class-wide analytics: class average, highest/lowest scores, grade distribution histogram, pass/fail rates.
- **User Interfaces & Exports:**
  - **Interactive Terminal CLI** with 11 commands and ASCII tables.
  - **Desktop Graphical UI (Tkinter)** with real-time input forms and modal report card dialogs.
  - **JSON Persistence:** Automatically saves and loads records from `students_data.json`.
  - **CSV Export:** Exports formatted grade summary to `grade_report.csv`.
  - **Sample Data Preloading:** One-click sample cohort setup for quick demonstration.

---

## Grading Scale & GPA Scheme

| Percentage Range | Letter Grade | GPA (4.0 Scale) | Classification | Academic Standing |
|:---:|:---:|:---:|:---|:---:|
| **90.00% – 100.00%** | **A** | **4.0** | Excellent / Outstanding | **PASS** |
| **80.00% – 89.99%** | **B** | **3.0** | Good / Commendable | **PASS** |
| **70.00% – 79.99%** | **C** | **2.0** | Satisfactory / Average | **PASS** |
| **60.00% – 69.99%** | **D** | **1.0** | Sufficient / Marginal | **PASS** |
| **0.00% – 59.99%** | **F** | **0.0** | Fail / Unsatisfactory | **FAIL** |

---

## Input Validation Rules & Boundaries

| Field | Validation Rule | Accepted Examples | Rejected Examples |
|:---|:---|:---|:---|
| **Student ID** | 2–20 characters, alphanumeric, hyphens, underscores | `S101`, `STU-001`, `CS_2026` | `S@101` (symbols), `A` (too short), blank |
| **Student Name** | 2–60 characters, letters, spaces, hyphens, apostrophes | `Ada Lovelace`, `Mary-Jane O'Connor` | `12345` (numbers), `John#` (symbols), blank |
| **Subject Name** | 2–50 characters, letters, numbers, spaces | `Mathematics`, `Computer Science 101` | `?` (symbols), blank |
| **Mark / Score** | Numeric float within $[0.00, 100.00]$ | `0.0`, `75.5`, `92.0`, `100.0` | `-5.0` (negative), `105.0` (overflow), `abc` (text) |

---

## Project Structure (System Only)

```
c:\sps\
│── run.py                  <- Application entry point (CLI and GUI launcher)
│── demo.py                 <- Automated system demonstration script
│── students_data.json      <- JSON database for student records
│── grade_report.csv        <- Exported grade reports in CSV format
│── README.md               <- System overview, grading schemas, and usage guide
│── .gitignore              <- Excludes PDF, generator scripts, and docs
│
├── grade_system\           <- Core application package
│   ├── __init__.py         <- Package exports
│   ├── models.py           <- Domain models (Student, SubjectScore, Grading)
│   ├── validator.py        <- Input validation engine
│   ├── grade_manager.py    <- Business logic & class analytics
│   ├── storage.py          <- JSON persistence & CSV exporter
│   ├── cli.py              <- Interactive terminal user interface
│   └── gui.py              <- Desktop graphical user interface (Tkinter)
│
└── tests\                  <- Automated test suite
    ├── __init__.py
    └── test_grade_system.py<- 16 unit tests (100% pass rate)
```

---

## Quick Start Instructions

### 1. Launch the Interactive Terminal CLI (Default)
```powershell
python run.py
```

### 2. Launch the Desktop Graphical User Interface (GUI)
```powershell
python run.py --gui
```

### 3. Run the Automated System Walkthrough Demo
```powershell
python demo.py
```

### 4. Run the Automated Unit Test Suite
```powershell
python -m unittest discover tests
```

---

## Sample Terminal Output

### Official Academic Report Card
```text
============================================================
  OFFICIAL ACADEMIC REPORT CARD
============================================================
  Student ID : S101
  Full Name  : Emma Watson
------------------------------------------------------------
  Subject                      Mark       Grade    GPA    Result  
------------------------------------------------------------
  Chemistry                    89.00      B        3.0    PASS    
  English                      96.00      A        4.0    PASS    
  Mathematics                  94.50      A        4.0    PASS    
  Physics                      91.00      A        4.0    PASS    
------------------------------------------------------------
  Cumulative Average : 92.62%
  Overall Grade      : A
  Cumulative GPA     : 3.75 / 4.00
  Academic Standing  : PASSED
============================================================
```

---

## Author & Environment
- **Author:** `mikezewdu5`
- **Environment:** Python 3.10+ (tested on Python 3.14)
- **Repository:** [https://github.com/mikezewdu5/class-grade-system](https://github.com/mikezewdu5/class-grade-system)
- **Release Version:** `v1.1.0` (Updated: November 11, 2026)
