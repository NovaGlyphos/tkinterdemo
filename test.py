import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3

class StudentMarksManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Marks Management System")
        self.root.geometry("800x600")

        # Database Setup
        self.conn = sqlite3.connect('student_marks.db')
        self.create_table()

        # UI Components
        self.create_input_form()
        self.create_student_list()
        self.create_analysis_section()

    def create_table(self):
        """Create SQLite table for storing student marks"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                name TEXT,
                roll_no TEXT UNIQUE,
                maths INTEGER,
                science INTEGER,
                hindi INTEGER,
                english INTEGER,
                sst INTEGER
            )
        ''')
        self.conn.commit()

    def create_input_form(self):
        """Create input form for student details and marks"""
        input_frame = tk.LabelFrame(self.root, text="Student Marks Entry", padx=10, pady=10)
        input_frame.pack(padx=10, pady=10, fill='x')

        # Labels and Entry Fields
        labels = ['Name', 'Roll No', 'Maths', 'Science', 'Hindi', 'English', 'SST']
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(input_frame, text=label).grid(row=i//4, column=(i%4)*2, padx=5, pady=5)
            entry = tk.Entry(input_frame, width=15)
            entry.grid(row=i//4, column=(i%4)*2+1, padx=5, pady=5)
            self.entries[label.lower()] = entry

        # Submit Button
        submit_btn = tk.Button(input_frame, text="Submit", command=self.save_student_data)
        submit_btn.grid(row=2, column=6, padx=10, pady=10)

    def create_student_list(self):
        """Create a treeview to display student records"""
        self.tree = ttk.Treeview(self.root, columns=(
            'Name', 'Roll No', 'Maths', 'Science', 'Hindi', 'English', 'SST', 
            'Total', 'Percentage', 'Grade'
        ), show='headings')

        for col in self.tree['columns']:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80, anchor='center')

        self.tree.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Buttons for actions
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(padx=10, pady=5)

        tk.Button(btn_frame, text="Refresh List", command=self.load_students).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_student).pack(side=tk.LEFT, padx=5)

    def create_analysis_section(self):
        """Create section for overall analysis"""
        analysis_frame = tk.LabelFrame(self.root, text="Class Analysis", padx=10, pady=10)
        analysis_frame.pack(padx=10, pady=10, fill='x')

        self.analysis_labels = {
            'total_students': tk.Label(analysis_frame, text="Total Students: 0"),
            'avg_percentage': tk.Label(analysis_frame, text="Average Percentage: 0%"),
            'top_performer': tk.Label(analysis_frame, text="Top Performer: N/A"),
            'lowest_performer': tk.Label(analysis_frame, text="Lowest Performer: N/A")
        }

        row, col = 0, 0
        for label in self.analysis_labels.values():
            label.grid(row=row, column=col, padx=5, pady=5)
            col += 1
            if col > 1:
                col = 0
                row += 1

        tk.Button(analysis_frame, text="Analyze Class", command=self.analyze_class).grid(row=row+1, column=0, columnspan=2, pady=10)

    def save_student_data(self):
        """Save student data to database"""
        try:
            data = {key: entry.get() for key, entry in self.entries.items()}
            
            # Validate inputs
            if not all(data.values()):
                messagebox.showerror("Error", "Please fill all fields")
                return

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO students 
                (name, roll_no, maths, science, hindi, english, sst) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['name'], data['roll no'], 
                int(data['maths']), int(data['science']), 
                int(data['hindi']), int(data['english']), 
                int(data['sst'])
            ))
            self.conn.commit()

            # Clear entries
            for entry in self.entries.values():
                entry.delete(0, tk.END)

            messagebox.showinfo("Success", "Student data saved successfully!")
            self.load_students()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def load_students(self):
        """Load students into treeview"""
        # Clear existing items
        for i in self.tree.get_children():
            self.tree.delete(i)

        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM students')
        
        for row in cursor.fetchall():
            # Calculate total and percentage
            total = sum(row[3:8])
            percentage = (total / 500) * 100

            # Determine grade
            grade = self.calculate_grade(percentage)

            # Insert into treeview
            self.tree.insert('', 'end', values=(
                row[1], row[2], row[3], row[4], row[5], row[6], row[7], 
                total, f"{percentage:.2f}%", grade
            ))

    def delete_student(self):
        """Delete selected student"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a student to delete")
            return

        roll_no = self.tree.item(selected[0])['values'][1]
        
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM students WHERE roll_no = ?', (roll_no,))
        self.conn.commit()

        messagebox.showinfo("Success", "Student deleted successfully")
        self.load_students()

    def analyze_class(self):
        """Perform class-level analysis"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM students')
        students = cursor.fetchall()

        if not students:
            messagebox.showinfo("Analysis", "No students in the database")
            return

        total_students = len(students)
        total_percentages = []

        for student in students:
            total = sum(student[3:8])
            percentage = (total / 500) * 100
            total_percentages.append(percentage)

        avg_percentage = sum(total_percentages) / total_students

        # Find top and lowest performers
        top_student = max(students, key=lambda x: sum(x[3:8]))
        lowest_student = min(students, key=lambda x: sum(x[3:8]))

        # Update analysis labels
        self.analysis_labels['total_students'].config(text=f"Total Students: {total_students}")
        self.analysis_labels['avg_percentage'].config(text=f"Average Percentage: {avg_percentage:.2f}%")
        self.analysis_labels['top_performer'].config(text=f"Top Performer: {top_student[1]} ({top_student[2]})")
        self.analysis_labels['lowest_performer'].config(text=f"Lowest Performer: {lowest_student[1]} ({lowest_student[2]})")

    def calculate_grade(self, percentage):
        """Calculate grade based on percentage"""
        if percentage >= 90:
            return 'A+'
        elif percentage >= 80:
            return 'A'
        elif percentage >= 70:
            return 'B+'
        elif percentage >= 60:
            return 'B'
        elif percentage >= 50:
            return 'C'
        elif percentage >= 40:
            return 'D'
        else:
            return 'F'

    def __del__(self):
        """Close database connection"""
        self.conn.close()

def main():
    root = tk.Tk()
    app = StudentMarksManagementSystem(root)
    root.mainloop()

if __name__ == "__main__":
    main()