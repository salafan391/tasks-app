import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget,QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from datetime import datetime
import sqlite3
import requests


class User(QWidget):
    def __init__(self):
        super(User, self).__init__()
        layout = QVBoxLayout()

        self.username_label = QLabel("اسم المستخدم")
        self.username_entry = QLineEdit()
        self.password_label = QLabel("كلمة المرور")
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.submit_button = QPushButton('حفظ')

        self.username_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.password_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.submit_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                font-size: 18px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

        self.submit_button.clicked.connect(self.save_users)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_entry)
        layout.addWidget(self.submit_button)
        self.setLayout(layout)

        self.conn = sqlite3.connect('tasks.db')
        self.curr = self.conn.cursor()
        self.create_table()
        self.display_name()
    def create_table(self):
        self.curr.execute('''
        CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY,
        name TEXT,
        password TEXT)
        ''')

    def user_exists(self):
        self.curr.execute('select * from users')
        user = self.curr.fetchone()
        return user

    def save_users(self):
        username = self.username_entry.text()
        password = self.password_entry.text()
        if self.user_exists():
            database_password = self.curr.execute('select password from users').fetchone()[0]
            print(database_password)
            print(password)
            if password == database_password :
                self.curr.execute(
                    'UPDATE users SET name = ?, password = ? WHERE id = 1', (username, password))
            else:
                QMessageBox.critical(None, "Error", "ليس لديك صلاحية التغيير")

        else:
            self.curr.execute(
                'INSERT INTO users (name, password) VALUES (?, ?)', (username, password))
        self.conn.commit()
        self.username_entry.clear()
        self.password_entry.clear()

    def display_name(self):
        name = self.curr.execute('SELECT name FROM users WHERE id = 1').fetchone()
        if name is not None:
            self.username_entry.setText(name[0])


class EmployeeTrackerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Employee Tracker")
        self.setGeometry(120, 120, 800, 600)
        self.employees = {}
        
        layout = QVBoxLayout()
        
        self.arrival_button = QPushButton("حضور", self)
        self.arrival_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: none;
                color: white;
                padding: 10px 20px;
                font-size: 18px;
            }
            
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.arrival_button.clicked.connect(self.mark_arrival)

        self.departure_button = QPushButton("انصراف", self)
        self.departure_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                border: none;
                color: white;
                padding: 10px 20px;
                font-size: 18px;
            }
            
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        self.departure_button.clicked.connect(self.mark_departure)
        # Create database connection
        self.conn = sqlite3.connect("tasks.db")
        self.curr = self.conn.cursor()
        self.curr.execute('''SELECT name from users''')
        result = self.curr.fetchone()
        self.employee_name = result[0] if result is not None else 'يرجى تسجيل مستخدم'
        self.hello_label = QLabel(f'أهلا {self.employee_name}', self)

        self.hello_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        self.hello_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.hello_label) 
        layout.addWidget(self.arrival_button)        
        layout.addWidget(self.departure_button)
        
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.create_table()
        self.fetch_attend_data()
        self.fetch_leave_data()
    def create_table(self):
        self.curr.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                arrival_time TEXT,
                departure_time TEXT
            )
        """)
        self.conn.commit()

    def fetch_attend_data(self):
        try:
            data = self.curr.execute(
                'SELECT max(date(arrival_time)) FROM employees').fetchall()[0][0]
            return data
        except IndexError:
            print('index error')

    def fetch_leave_data(self):
        try:
            data = self.curr.execute(
                'SELECT departure_time FROM employees').fetchall()
            if data[len(data)-1][0] != None:
                return data[len(data)-1][0].split()[0]
        except IndexError:
            print('index error')

    def mark_arrival(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if current_time.split()[0] != self.fetch_attend_data():
            if self.employee_name:
                self.curr.execute("""
                    INSERT INTO employees (name, arrival_time)
                    VALUES (?, ?)
                """, (self.employee_name, current_time))
                self.conn.commit()

                self.post_to_sheety(self.employee_name,
                                    current_time, "حضور")
            self.hello_label.setText(f"{self.employee_name} الوصول عند {current_time}")
        else:
            self.hello_label.setText('لقد تم التحضير بالفعل')

    def mark_departure(self):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        splitted = current_time.split()[0]
        if splitted != self.fetch_leave_data():
            if self.employee_name:
                self.curr.execute("""
                    UPDATE employees
                    SET departure_time = ?
                    WHERE name = ?
                    AND departure_time IS NULL
                """, (current_time, self.employee_name))
                self.conn.commit()

                self.post_to_sheety(self.employee_name,
                                    current_time, "انصراف")

                
            self.hello_label.setText(f"{self.employee_name} تم الانصراف {current_time}")
        else:
            self.hello_label.setText('لقد تم الانصراف بالفعل')
    def post_to_sheety(self, name, timestamp, status):
        endpoint = "https://api.sheety.co/703ebec0ffe37186258ccfb2f09eafc0/employee/1"
        headers = {
            "Authorization": "Bearer Ahmd605108",
            "Content-Type": "application/json"
        }
        data = {
            "1": {
                "name": name,
                "timestamp": timestamp,
                "status": status
            }
        }
        response = requests.post(endpoint, headers=headers, json=data)
        if response.status_code == 200:
            print("Data posted to Sheety successfully.")
        else:
            print("Failed to post data to Sheety.")

