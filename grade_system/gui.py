"""
Student Grade Management System - Desktop Graphical User Interface (GUI)
Built using Python's standard Tkinter & ttk libraries.
Allows visual data entry, real-time input validation, interactive tables,
detailed student report card dialogs, analytics, and CSV/PDF export.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import sys
import os

from .grade_manager import GradeManager
from .storage import StorageManager
from .validator import InputValidator, ValidationError


class GradeSystemGUI(tk.Tk):
    """Main Application Window for Student Grade Management System."""

    def __init__(self, data_file: str = "students_data.json"):
        super().__init__()
        self.title("Student Grade Management System (SGMS)")
        self.geometry("980x680")
        self.minsize(850, 550)

        # Apply system styling
        self.style = ttk.Style(self)
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.manager = GradeManager()
        self.storage = StorageManager(data_file)
        self.storage.load_from_file(self.manager)

        self._configure_styles()
        self._build_ui()
        self.refresh_table()

    def _configure_styles(self):
        self.style.configure("Header.TLabel", font=("Helvetica", 14, "bold"), foreground="#1A365D")
        self.style.configure("Subheader.TLabel", font=("Helvetica", 10), foreground="#4A5568")
        self.style.configure("Treeview.Heading", font=("Helvetica", 9, "bold"), foreground="#1A365D")
        self.style.configure("Treeview", font=("Helvetica", 9), rowheight=24)
        self.style.configure("Action.TButton", font=("Helvetica", 9, "bold"))

    def _build_ui(self):
        # Top Header Banner
        header_frame = ttk.Frame(self, padding=(16, 12))
        header_frame.pack(fill=tk.X)

        title_lbl = ttk.Label(header_frame, text="Student Grade Management System", style="Header.TLabel")
        title_lbl.pack(anchor=tk.W)

        sub_lbl = ttk.Label(
            header_frame,
            text="Personal Software Process (PSP0.1) • Mark Recording, Average & Grade Engine, Validation & Reporting",
            style="Subheader.TLabel"
        )
        sub_lbl.pack(anchor=tk.W)

        # Main Split Panes: Left (Forms) and Right (Data View & Analytics)
        container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        container.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        # LEFT PANE: Input Forms
        left_frame = ttk.Frame(container, padding=10, width=320)
        container.add(left_frame, weight=1)

        # 1. Enroll Student Card
        enroll_box = ttk.LabelFrame(left_frame, text=" 1. Enroll New Student ", padding=10)
        enroll_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(enroll_box, text="Student ID (e.g. S107):").pack(anchor=tk.W)
        self.entry_student_id = ttk.Entry(enroll_box)
        self.entry_student_id.pack(fill=tk.X, pady=(2, 6))

        ttk.Label(enroll_box, text="Full Name:").pack(anchor=tk.W)
        self.entry_name = ttk.Entry(enroll_box)
        self.entry_name.pack(fill=tk.X, pady=(2, 8))

        btn_enroll = ttk.Button(enroll_box, text="Enroll Student", command=self.on_enroll_student)
        btn_enroll.pack(fill=tk.X)

        # 2. Add / Update Mark Card
        mark_box = ttk.LabelFrame(left_frame, text=" 2. Record Subject Mark ", padding=10)
        mark_box.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(mark_box, text="Target Student ID:").pack(anchor=tk.W)
        self.entry_mark_sid = ttk.Entry(mark_box)
        self.entry_mark_sid.pack(fill=tk.X, pady=(2, 6))

        ttk.Label(mark_box, text="Subject Name (e.g. Mathematics):").pack(anchor=tk.W)
        self.entry_subject = ttk.Entry(mark_box)
        self.entry_subject.pack(fill=tk.X, pady=(2, 6))

        ttk.Label(mark_box, text="Mark / Score (0.00 – 100.00):").pack(anchor=tk.W)
        self.entry_score = ttk.Entry(mark_box)
        self.entry_score.pack(fill=tk.X, pady=(2, 8))

        btn_save_mark = ttk.Button(mark_box, text="Record / Update Mark", command=self.on_record_mark)
        btn_save_mark.pack(fill=tk.X)

        # 3. Quick Actions
        actions_box = ttk.LabelFrame(left_frame, text=" Quick Actions ", padding=10)
        actions_box.pack(fill=tk.X, pady=(0, 10))

        btn_seed = ttk.Button(actions_box, text="Preload Sample Dataset", command=self.on_seed_data)
        btn_seed.pack(fill=tk.X, pady=2)

        btn_export_csv = ttk.Button(actions_box, text="Export Grade Report (CSV)", command=self.on_export_csv)
        btn_export_csv.pack(fill=tk.X, pady=2)

        btn_compile_pdf = ttk.Button(actions_box, text="Recompile PDF Report", command=self.on_recompile_pdf)
        btn_compile_pdf.pack(fill=tk.X, pady=2)

        btn_delete = ttk.Button(actions_box, text="Delete Selected Student", command=self.on_delete_student)
        btn_delete.pack(fill=tk.X, pady=2)

        # RIGHT PANE: Search, Table, and Class Analytics
        right_frame = ttk.Frame(container, padding=10)
        container.add(right_frame, weight=3)

        # Search Bar
        search_frame = ttk.Frame(right_frame)
        search_frame.pack(fill=tk.X, pady=(0, 8))

        ttk.Label(search_frame, text="Search (ID/Name):", font=("Helvetica", 9, "bold")).pack(side=tk.LEFT, padx=(0, 6))
        self.entry_search = ttk.Entry(search_frame)
        self.entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))
        self.entry_search.bind("<KeyRelease>", lambda e: self.on_search())

        btn_refresh = ttk.Button(search_frame, text="Clear / Refresh", command=self.refresh_table)
        btn_refresh.pack(side=tk.RIGHT)

        # Student Records Table (Treeview)
        table_frame = ttk.Frame(right_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("rank", "id", "name", "subjects", "average", "grade", "gpa", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("rank", text="Rank")
        self.tree.heading("id", text="Student ID")
        self.tree.heading("name", text="Full Name")
        self.tree.heading("subjects", text="Subjects")
        self.tree.heading("average", text="Average Mark")
        self.tree.heading("grade", text="Grade")
        self.tree.heading("gpa", text="GPA")
        self.tree.heading("status", text="Status")

        self.tree.column("rank", width=50, anchor=tk.CENTER)
        self.tree.column("id", width=90, anchor=tk.CENTER)
        self.tree.column("name", width=180, anchor=tk.W)
        self.tree.column("subjects", width=70, anchor=tk.CENTER)
        self.tree.column("average", width=100, anchor=tk.CENTER)
        self.tree.column("grade", width=60, anchor=tk.CENTER)
        self.tree.column("gpa", width=60, anchor=tk.CENTER)
        self.tree.column("status", width=75, anchor=tk.CENTER)

        tree_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=tree_scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind("<Double-1>", lambda e: self.on_view_report_card())

        # Bottom Bar: Summary Stats & Report Card Button
        bottom_frame = ttk.Frame(right_frame, padding=(0, 8))
        bottom_frame.pack(fill=tk.X)

        self.lbl_stats = ttk.Label(
            bottom_frame,
            text="Total Students: 0 | Class Average: 0.00% | Pass Rate: 0.0%",
            font=("Helvetica", 9, "bold"),
            foreground="#2B6CB0"
        )
        self.lbl_stats.pack(side=tk.LEFT)

        btn_card = ttk.Button(bottom_frame, text="View Detailed Report Card", style="Action.TButton", command=self.on_view_report_card)
        btn_card.pack(side=tk.RIGHT)

    def refresh_table(self, students=None):
        """Populates the table with ranked student data and updates summary bar."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        if students is None:
            students = self.manager.get_ranked_students()

        for rank, s in enumerate(students, start=1):
            avg = s.calculate_average()
            grade = s.get_overall_grade()
            gpa = s.get_overall_gpa()
            status = "PASS" if s.is_passing() else "FAIL"

            self.tree.insert(
                "",
                tk.END,
                values=(rank, s.student_id, s.name, len(s.scores), f"{avg:.2f}%", grade, f"{gpa:.2f}", status)
            )

        # Update stats
        stats = self.manager.calculate_class_statistics()
        if stats["total_students"] > 0:
            self.lbl_stats.config(
                text=f"Total: {stats['total_students']} | Class Avg: {stats['class_average']:.2f}% | "
                     f"High: {stats['highest_average']:.2f}% | Pass Rate: {stats['pass_rate_pct']:.1f}%"
            )
        else:
            self.lbl_stats.config(text="No student records enrolled.")

    def on_search(self):
        kw = self.entry_search.get().strip()
        if not kw:
            self.refresh_table()
        else:
            filtered = self.manager.search_students(kw)
            # Maintain ranking order among search results
            ranked_filtered = sorted(filtered, key=lambda s: s.calculate_average(), reverse=True)
            self.refresh_table(ranked_filtered)

    def on_enroll_student(self):
        raw_id = self.entry_student_id.get()
        raw_name = self.entry_name.get()

        valid_id, clean_id, err_id = InputValidator.validate_student_id(raw_id)
        if not valid_id:
            messagebox.showerror("Input Validation Error", err_id, parent=self)
            return

        valid_name, clean_name, err_name = InputValidator.validate_name(raw_name)
        if not valid_name:
            messagebox.showerror("Input Validation Error", err_name, parent=self)
            return

        if self.manager.get_student(clean_id):
            messagebox.showerror("Duplicate Student", f"Student ID '{clean_id}' already exists in registry.", parent=self)
            return

        try:
            self.manager.add_student(clean_id, clean_name)
            self.storage.save_to_file(self.manager)
            self.refresh_table()

            # Pre-fill mark target ID
            self.entry_mark_sid.delete(0, tk.END)
            self.entry_mark_sid.insert(0, clean_id)
            self.entry_student_id.delete(0, tk.END)
            self.entry_name.delete(0, tk.END)

            messagebox.showinfo("Enrollment Success", f"Student '{clean_name}' ({clean_id}) enrolled successfully!", parent=self)
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e), parent=self)

    def on_record_mark(self):
        raw_sid = self.entry_mark_sid.get().strip().upper()
        raw_sub = self.entry_subject.get().strip()
        raw_score = self.entry_score.get().strip()

        student = self.manager.get_student(raw_sid)
        if not student:
            messagebox.showerror("Student Not Found", f"Student with ID '{raw_sid}' does not exist.", parent=self)
            return

        valid_sub, clean_sub, err_sub = InputValidator.validate_subject(raw_sub)
        if not valid_sub:
            messagebox.showerror("Subject Validation Error", err_sub, parent=self)
            return

        valid_mark, clean_mark, err_mark = InputValidator.validate_mark(raw_score)
        if not valid_mark:
            messagebox.showerror("Mark Validation Error", err_mark, parent=self)
            return

        score_obj = self.manager.add_or_update_mark(raw_sid, clean_sub, clean_mark)
        self.storage.save_to_file(self.manager)
        self.refresh_table()

        self.entry_subject.delete(0, tk.END)
        self.entry_score.delete(0, tk.END)

        messagebox.showinfo(
            "Mark Recorded",
            f"Recorded for {student.name} ({student.student_id}):\n\n"
            f"Subject: {score_obj.subject}\n"
            f"Mark: {score_obj.mark:.2f}%\n"
            f"Letter Grade: {score_obj.letter_grade}\n"
            f"Grade Point (GPA): {score_obj.gpa_point:.1f}\n"
            f"Status: {'PASS' if score_obj.passed else 'FAIL'}",
            parent=self
        )

    def on_view_report_card(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student from the table first.", parent=self)
            return

        item = self.tree.item(selected[0])
        student_id = item["values"][1]
        student = self.manager.get_student(str(student_id))
        if not student:
            return

        # Modal Dialog
        dialog = tk.Toplevel(self)
        dialog.title(f"Report Card: {student.name} ({student.student_id})")
        dialog.geometry("520x420")
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(dialog, text="OFFICIAL ACADEMIC REPORT CARD", font=("Helvetica", 12, "bold"), foreground="#1A365D").pack(pady=(12, 4))
        ttk.Label(dialog, text=f"Student ID: {student.student_id}  |  Name: {student.name}", font=("Helvetica", 10)).pack(pady=(0, 10))

        # Table of subjects
        sub_tree = ttk.Treeview(dialog, columns=("sub", "mark", "grade", "gpa", "status"), show="headings", height=8)
        sub_tree.heading("sub", text="Subject")
        sub_tree.heading("mark", text="Mark")
        sub_tree.heading("grade", text="Grade")
        sub_tree.heading("gpa", text="GPA")
        sub_tree.heading("status", text="Result")

        sub_tree.column("sub", width=180, anchor=tk.W)
        sub_tree.column("mark", width=80, anchor=tk.CENTER)
        sub_tree.column("grade", width=60, anchor=tk.CENTER)
        sub_tree.column("gpa", width=60, anchor=tk.CENTER)
        sub_tree.column("status", width=70, anchor=tk.CENTER)

        for sub, score in sorted(student.scores.items()):
            res = "PASS" if score.passed else "FAIL"
            sub_tree.insert("", tk.END, values=(score.subject, f"{score.mark:.2f}%", score.letter_grade, f"{score.gpa_point:.1f}", res))

        sub_tree.pack(fill=tk.BOTH, expand=True, padx=16, pady=6)

        # Summary Footnote
        summary_frame = ttk.Frame(dialog, padding=12)
        summary_frame.pack(fill=tk.X)

        avg = student.calculate_average()
        grade = student.get_overall_grade()
        gpa = student.get_overall_gpa()
        standing = "PASSED" if student.is_passing() else "FAILED"

        txt = (
            f"Cumulative Average: {avg:.2f}%    |    Overall Grade: {grade}\n"
            f"Cumulative GPA: {gpa:.2f} / 4.00    |    Academic Standing: {standing}"
        )
        ttk.Label(summary_frame, text=txt, font=("Helvetica", 9, "bold"), foreground="#2B6CB0").pack(pady=(0, 8))
        ttk.Button(summary_frame, text="Close Report Card", command=dialog.destroy).pack()

    def on_delete_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Required", "Please select a student from the table to delete.", parent=self)
            return

        item = self.tree.item(selected[0])
        student_id = str(item["values"][1])
        student_name = item["values"][2]

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete student '{student_name}' ({student_id})?",
            parent=self
        )
        if confirm:
            self.manager.remove_student(student_id)
            self.storage.save_to_file(self.manager)
            self.refresh_table()
            messagebox.showinfo("Deleted", f"Student '{student_id}' has been removed.", parent=self)

    def on_seed_data(self):
        count = self.storage.seed_sample_data(self.manager)
        self.storage.save_to_file(self.manager)
        self.refresh_table()
        messagebox.showinfo("Dataset Preloaded", f"Loaded {count} sample student records with authentic marks.", parent=self)

    def on_export_csv(self):
        filename = filedialog.asksaveasfilename(
            parent=self,
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile="grade_report.csv"
        )
        if filename:
            success = self.storage.export_summary_csv(self.manager, filename)
            if success:
                messagebox.showinfo("Export Successful", f"Grade report successfully saved to:\n{filename}", parent=self)
            else:
                messagebox.showerror("Export Failed", "Could not export CSV file.", parent=self)

    def on_recompile_pdf(self):
        try:
            cmd = [sys.executable, "generate_report_pdf.py"]
            subprocess.run(cmd, check=True)
            messagebox.showinfo(
                "PDF Recompiled",
                "Successfully generated publication-grade PDF report:\n\nStudent_Grade_Management_System_Project_Report.pdf",
                parent=self
            )
        except Exception as e:
            messagebox.showerror("PDF Compilation Error", str(e), parent=self)


def launch_gui():
    app = GradeSystemGUI()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()

