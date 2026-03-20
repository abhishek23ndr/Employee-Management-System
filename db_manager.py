import pymongo
import csv
import os

class DatabaseManager:
    def __init__(self):
        # Connect to local MongoDB instance
        atlas_uri = "mongodb+srv://adminAbhishek:abhishek_GUI@cluster0.fincze7.mongodb.net/?appName=Cluster0"
        self.client = pymongo.MongoClient(atlas_uri)
        # Create/Connect to database 'company_db'
        self.db = self.client["company_db"]
        # Create/Connect to collection 'employees'
        self.collection = self.db["employees"]

        self._auto_load_csv("employees.csv")

    def _auto_load_csv(self, filepath):
        """Automatically load data from CSV if the database is currently empty."""
        print("--- Checking CSV Auto-Load Status ---")
        
        # Check if the database already has data
        doc_count = self.collection.count_documents({})
        if doc_count > 0:
            print(f"Skipping: Database already has {doc_count} employees in it.")
            return

        # Check if the CSV file exists in the folder
        if not os.path.exists(filepath):
            print(f"Skipping: ERROR! Could not find '{filepath}' in this folder.")
            return
            
        print("Database is empty and file found. Auto-loading data from CSV...")
        formatted_data = []
        try:
            with open(filepath, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    employee_doc = {
                        "emp_id": str(row['EMPLOYEE_ID']),
                        "name": f"{row['FIRST_NAME']} {row['LAST_NAME']}",
                        "department": row['JOB_ID'],
                        "salary": float(row['SALARY'])
                    }
                    formatted_data.append(employee_doc)

            # Insert all records into MongoDB
            if formatted_data:
                self.collection.insert_many(formatted_data)
                print("Auto-load complete! 50 employees added.")
        except Exception as e:
            print(f"Error auto-loading CSV: {e}")

    # --- YOUR MANUAL CRUD OPERATIONS BELOW ---

    def insert_employee(self, emp_id, name, department, salary):
        """CREATE: Add a new employee."""
        # Check if ID already exists
        if self.collection.find_one({"emp_id": emp_id}):
            return False 
        
        data = {"emp_id": emp_id, "name": name, "department": department, "salary": salary}
        self.collection.insert_one(data)
        return True

    def fetch_employees(self):
        """READ: Fetch all employees."""
        return list(self.collection.find({}, {"_id": 0})) # Exclude MongoDB's default _id

    def search_employee(self, search_term):
        """READ: Search by Employee ID or Name."""
        query = {"$or": [{"emp_id": search_term}, {"name": {"$regex": search_term, "$options": "i"}}]}
        return list(self.collection.find(query, {"_id": 0}))

    def update_employee(self, emp_id, new_name, new_dept, new_salary):
        """UPDATE: Update an existing employee's details."""
        query = {"emp_id": emp_id}
        new_values = {"$set": {"name": new_name, "department": new_dept, "salary": new_salary}}
        result = self.collection.update_one(query, new_values)
        return result.modified_count > 0

    def delete_employee(self, emp_id):
        """DELETE: Remove an employee."""
        result = self.collection.delete_one({"emp_id": emp_id})
        return result.deleted_count > 0