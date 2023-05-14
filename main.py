import tkinter as tk
import sqlite3
from tkinter import messagebox, ttk
import datetime


class TaskForm(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.grid()
        self.create_table
        self.create_widgets()

    def create_table(self):
        conn = sqlite3.connect('tasks.db')

# create a cursor
        c = conn.cursor()
        # create tasks table if it doesn't exist already
        c.execute("CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY,name text, status text,description text,,assignment text,date_created text);")

        # commit changes
        conn.commit()
        # close connection
        conn.close()

    def create_widgets(self):

        # Task name label and entry
        self.task_name_label = tk.Label(self, text="اسم المهمة")
        self.task_name_label.grid(column=1, row=0)
        self.task_name_entry = tk.Entry(self, width=50, justify='right')
        self.task_name_entry.grid(column=0, row=0, padx=10, pady=10)
        # Task status label and dropdown
        self.task_status_label = tk.Label(self, text="حالة المهمة")
        self.task_status_label.grid(column=1, row=1)
        self.task_status_dropdown = ttk.Combobox(
            self, justify='right', values=["غير منجزة", "منجزة"], width=50)
        self.task_status_dropdown.grid(column=0, row=1, padx=10, pady=10)
        # Task description label and entry
        self.task_desc_label = tk.Label(
            self, text="سبب عدم الإنجاز")
        self.task_desc_label.grid(column=1, row=2)
        self.task_desc_entry = tk.Entry(self, width=50, justify='right')
        self.task_desc_entry.grid(column=0, row=2, padx=10, pady=10)
        # Assignment label and entry
        self.assignment_label = tk.Label(
            self, text="المسؤول عن التنفيذ")
        self.assignment_label.grid(column=1, row=3)
        self.assignment_entry = tk.Entry(self, width=50, justify='right')
        self.assignment_entry.grid(column=0, row=3)

        # Submit button
        self.submit_button = tk.Button(
            self, text="إضافة", command=self.submit_form, width=20)
        self.submit_button.grid(column=1, row=4, padx=10, pady=10, sticky='W')

        # Update button
        self.update_button = tk.Button(
            self, text="تحديث", command=self.update_form, width=20)
        self.update_button.grid(column=0, row=4, sticky='W', padx=10)

        self.delete_task_button = tk.Button(
            self.master, text="حذف مهمة", command=self.delete_task)
        self.delete_task_button.grid(
            row=4, column=0, padx=20, pady=20, sticky='W')
        self.clear_task_button = tk.Button(
            self.master, text="تصفية", command=self.clear_task)
        self.clear_task_button.grid(row=4, column=0, padx=20, pady=20)
        # Task listbox
        self.tree = ttk.Treeview(root, column=(
            "c1", "c2", 'c3', "c4", "c5", 'c6'), show='headings')

        self.tree.column("#1", anchor=tk.CENTER)
        self.tree.heading("#1", text="رقم المهمة")

        self.tree.column("#2", anchor=tk.CENTER)
        self.tree.heading("#2", text="اسم المهمة")

        self.tree.column("#4", anchor=tk.CENTER)
        self.tree.heading("#4", text="الحالة")

        self.tree.column("#3", anchor=tk.CENTER)
        self.tree.heading("#3", text="سبب عدم الإنجاز")

        self.tree.column("#5", anchor=tk.CENTER)
        self.tree.heading("#5", text="الموظف")
        self.tree.column("#6", anchor=tk.CENTER)
        self.tree.heading("#6", text="التاريخ")

        self.tree.grid(row=6)
        self.tree.bind('<ButtonRelease-1>', self.load_selected_task)
        self.load_tasks()

    def check_data(self):
        task_name = self.task_name_entry.get()
        if len(task_name) == 0:
            return messagebox.showerror('Error', 'لا يوجد بيانات! ')

    def submit_form(self):
        # Retrieve form data
        task_name = self.task_name_entry.get()
        task_status = self.task_status_dropdown.get()
        task_desc = self.task_desc_entry.get()
        assignment = self.assignment_entry.get()
        date_created = datetime.datetime.now().date()
        if not self.check_data():
            # Save form data to database
            msg = messagebox.askyesno(
                'تأكيد', f" اسم المهمة {task_name}\n هل أنت متأكد من الإضافة")
            if msg:
                conn = sqlite3.connect("tasks.db")
                c = conn.cursor()
                c.execute("INSERT INTO tasks (name, description, status, assignment, date_created) VALUES (?, ?, ?, ?, ?)",
                          (task_name, task_desc, task_status, assignment, date_created))
                conn.commit()
                conn.close()
        # Clear form fields and reload tasks
                self.clear_task()
                self.load_tasks()

    def update_form(self):
        # Retrieve form data
        task_name = self.task_name_entry.get()
        task_desc = self.task_desc_entry.get()
        task_status = self.task_status_dropdown.get()
        assignment = self.assignment_entry.get()
        # Get selected task from listbox

        select = self.tree.focus()
        if not select:
            return
        task_id = self.tree.item(select)['values'][0]
        if not self.check_data():
            msg = messagebox.askyesno(
                'تأكيد', f" اسم المهمة {task_name}\n هل أنت متأكد من التحديث")
            # Update task in database
            if msg:
                conn = sqlite3.connect("tasks.db")
                c = conn.cursor()
                c.execute("UPDATE tasks SET name = ?, description = ?, status = ?, assignment = ? WHERE id = ?",
                          (task_name, task_desc, task_status, assignment, task_id,))
                conn.commit()
                conn.close()
                # Clear form fields and reload tasks
                self.clear_task()
                self.load_tasks()

    def delete_task(self):
        # Retrieve form data
        # Get selected task from listbox
        select = self.tree.focus()
        if not select:
            return
        task_id = self.tree.item(select)['values'][0]
        if not self.check_data():
            msg = messagebox.askyesno(
                'تأكيد', f" هل أنت متأكد من الحذف")
            # Update task in database
            if msg:
                conn = sqlite3.connect("tasks.db")
                c = conn.cursor()
                c.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
                conn.commit()
                conn.close()

            # Clear form fields and reload tasks
                self.clear_task()
                self.load_tasks()

    def load_tasks(self):
        self.tree.delete(*self.tree.get_children())
        # Load tasks from database and add to listbox
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        try:
            c.execute("SELECT * FROM tasks")
            rows = c.fetchall()
            for row in rows:
                self.tree.insert("", tk.END, values=(row))
            conn.close()
        except:
            print('ok')

    def load_selected_task(self, event):
        # Get selected task from listbox
        select = self.tree.focus()
        if not select:
            return
        task_id = self.tree.item(select)['values'][0]
        # Load selected task from database and display in form
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = c.fetchone()
        self.task_name_entry.delete(0, tk.END)
        self.task_name_entry.insert(0, row[1])
        self.task_desc_entry.delete(0, tk.END)
        self.task_desc_entry.insert(0, row[2])
        self.task_status_dropdown.set(row[3])
        self.assignment_entry.delete(0, tk.END)
        self.assignment_entry.insert(0, row[4])
        conn.close()

    def clear_task(self):
        self.task_name_entry.delete(0, tk.END)
        self.task_desc_entry.delete(0, tk.END)
        self.assignment_entry.delete(0, tk.END)
        self.task_status_dropdown.set("")
        for item in self.tree.selection():
            self.tree.selection_remove(item)


root = tk.Tk()
root.title("المهام اليومية")
photo = tk.PhotoImage(file='muasah.png')
root.iconphoto(False, photo)
form = TaskForm(master=root)
form.mainloop()
