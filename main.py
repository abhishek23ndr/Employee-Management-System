import tkinter as tk
from tkinter import ttk, messagebox
import csv
from db_manager import DatabaseManager

class EmployeeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Employee Management System")
        
        # 1. Set a default size and a minimum size so it doesn't get too squished
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)
        
        # 2. Automatically Maximize the window on launch!
        try:
            self.root.state('zoomed')
        except:
            pass # Fallback in case it's run on Mac/Linux

        self.db = DatabaseManager()

        # Variables for form entries
        self.emp_id_var = tk.StringVar()
        self.name_var = tk.StringVar()
        self.dept_var = tk.StringVar()
        self.salary_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self.create_gui()
        self.populate_table()

    def create_gui(self):
        # --- TITLE ---
        title = tk.Label(self.root, text="Employee Management System", font=("Arial", 20, "bold"), bg="#2c3e50", fg="white")
        title.pack(side=tk.TOP, fill=tk.X)

        # --- LEFT FRAME: Data Entry Form ---
        entry_frame = tk.Frame(self.root, bd=4, relief=tk.RIDGE, bg="#ecf0f1")
        # CHANGED: Using pack instead of place so it adjusts dynamically
        entry_frame.pack(side=tk.LEFT, fill=tk.Y, padx=20, pady=20)

        tk.Label(entry_frame, text="Manage Records", font=("Arial", 14, "bold"), bg="#ecf0f1").grid(row=0, columnspan=2, pady=10)

        tk.Label(entry_frame, text="Emp ID:", bg="#ecf0f1").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(entry_frame, textvariable=self.emp_id_var).grid(row=1, column=1, padx=10, pady=10)

        tk.Label(entry_frame, text="Name:", bg="#ecf0f1").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(entry_frame, textvariable=self.name_var).grid(row=2, column=1, padx=10, pady=10)

        tk.Label(entry_frame, text="Department:", bg="#ecf0f1").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(entry_frame, textvariable=self.dept_var).grid(row=3, column=1, padx=10, pady=10)

        tk.Label(entry_frame, text="Salary:", bg="#ecf0f1").grid(row=4, column=0, padx=10, pady=10, sticky="w")
        tk.Entry(entry_frame, textvariable=self.salary_var).grid(row=4, column=1, padx=10, pady=10)

        # Buttons Frame
        btn_frame = tk.Frame(entry_frame, bg="#ecf0f1")
        btn_frame.grid(row=5, columnspan=2, pady=20)

        tk.Button(btn_frame, text="Add", command=self.add_record, width=10, bg="#27ae60", fg="white").grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Update", command=self.update_record, width=10, bg="#2980b9", fg="white").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Delete", command=self.delete_record, width=10, bg="#c0392b", fg="white").grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Clear", command=self.clear_form, width=10).grid(row=1, column=1, padx=5, pady=5)

        # --- RIGHT FRAME: Table and Search ---
        data_frame = tk.Frame(self.root, bd=4, relief=tk.RIDGE)
        # CHANGED: fill=tk.BOTH and expand=True forces this frame to stretch out and fill the rest of the screen!
        data_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20), pady=20)

        # Search Bar
        search_frame = tk.Frame(data_frame)
        search_frame.pack(side=tk.TOP, fill=tk.X, pady=5, padx=5)
        tk.Label(search_frame, text="Search (ID/Name):").pack(side=tk.LEFT, padx=5)
        tk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_record).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Show All", command=self.populate_table).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Export CSV", command=self.export_csv).pack(side=tk.LEFT, padx=5)

        # Treeview (Table)
        scroll_y = tk.Scrollbar(data_frame, orient=tk.VERTICAL)
        self.employee_table = ttk.Treeview(data_frame, columns=("emp_id", "name", "dept", "salary"), yscrollcommand=scroll_y.set)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_y.config(command=self.employee_table.yview)

        self.employee_table.heading("emp_id", text="ID")
        self.employee_table.heading("name", text="Name")
        self.employee_table.heading("dept", text="Department")
        self.employee_table.heading("salary", text="Salary")
        self.employee_table['show'] = 'headings'
        
        self.employee_table.column("emp_id", width=50)
        self.employee_table.column("name", width=150)
        self.employee_table.column("dept", width=100)
        self.employee_table.column("salary", width=100)
        
        self.employee_table.pack(fill=tk.BOTH, expand=1)
        # Bind row selection to form filling
        self.employee_table.bind("<ButtonRelease-1>", self.fill_form_from_table)

    # --- LOGIC & VALIDATION ---
    def validate_inputs(self):
        if not self.emp_id_var.get() or not self.name_var.get() or not self.dept_var.get() or not self.salary_var.get():
            messagebox.showerror("Error", "All fields are required!")
            return False
        try:
            float(self.salary_var.get()) # Ensure salary is a number
        except ValueError:
            messagebox.showerror("Error", "Salary must be a number!")
            return False
        return True

    def add_record(self):
        if self.validate_inputs():
            success = self.db.insert_employee(
                self.emp_id_var.get(), self.name_var.get(), self.dept_var.get(), float(self.salary_var.get())
            )
            if success:
                messagebox.showinfo("Success", "Record added successfully")
                self.clear_form()
                self.populate_table()
            else:
                messagebox.showerror("Error", "Employee ID already exists!")

    def populate_table(self):
        # Clear existing rows
        for row in self.employee_table.get_children():
            self.employee_table.delete(row)
        # Fetch and insert
        for row in self.db.fetch_employees():
            self.employee_table.insert("", tk.END, values=(row["emp_id"], row["name"], row["department"], row["salary"]))

    def fill_form_from_table(self, event):
        selected_row = self.employee_table.focus()
        data = self.employee_table.item(selected_row, 'values')
        if data:
            self.emp_id_var.set(data[0])
            self.name_var.set(data[1])
            self.dept_var.set(data[2])
            self.salary_var.set(data[3])

    def update_record(self):
        if self.validate_inputs():
            success = self.db.update_employee(
                self.emp_id_var.get(), self.name_var.get(), self.dept_var.get(), float(self.salary_var.get())
            )
            if success:
                messagebox.showinfo("Success", "Record updated successfully")
                self.clear_form()
                self.populate_table()
            else:
                messagebox.showerror("Error", "Could not update record.")

    def delete_record(self):
        emp_id = self.emp_id_var.get()
        if not emp_id:
            messagebox.showerror("Error", "Please select a record to delete.")
            return
            
        # Confirmation Dialog
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Employee ID {emp_id}?")
        if confirm:
            if self.db.delete_employee(emp_id):
                messagebox.showinfo("Success", "Record deleted successfully")
                self.clear_form()
                self.populate_table()
            else:
                messagebox.showerror("Error", "Record not found.")

    def search_record(self):
        term = self.search_var.get()
        if not term:
            self.populate_table()
            return
        for row in self.employee_table.get_children():
            self.employee_table.delete(row)
        for row in self.db.search_employee(term):
             self.employee_table.insert("", tk.END, values=(row["emp_id"], row["name"], row["department"], row["salary"]))

    def clear_form(self):
        self.emp_id_var.set("")
        self.name_var.set("")
        self.dept_var.set("")
        self.salary_var.set("")

    def export_csv(self):
        data = self.db.fetch_employees()
        if not data:
            messagebox.showinfo("Info", "No data to export.")
            return
        try:
            with open("employees_export.csv", "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(["Emp ID", "Name", "Department", "Salary"])
                for row in data:
                    writer.writerow([row["emp_id"], row["name"], row["department"], row["salary"]])
            messagebox.showinfo("Success", "Data exported to employees_export.csv")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = EmployeeApp(root)
    root.mainloop()