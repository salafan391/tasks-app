import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QPushButton, \
    QLineEdit, QComboBox, QTableWidget, QTableWidgetItem, QMessageBox, QStyledItemDelegate,QTabWidget
from PyQt5.QtGui import QColor, QFont, QIcon, QCursor
from PyQt5.QtCore import Qt, QDateTime
import sqlite3
from test import *


class HoverButton(QPushButton):
    def __init__(self, text):
        super().__init__(text)

    def enterEvent(self, event):
        self.setCursor(QCursor(Qt.PointingHandCursor))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.unsetCursor()
        super().leaveEvent(event)


class BorderDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        painter.save()

        # Set text color based on the status
        if index.column() == 3:  # Column index of the status
            status = index.data()
            if status == "منجزة":
                # Green text color for status 'أنجزت'
                painter.setPen(QColor("#00FF00"))
            elif status == 'منجزة':
                painter.setPen(QColor("#00FF00"))

            else:
                # Red text color for other statuses
                painter.setPen(QColor("#FF0000"))
        else:
            # Black text color for other columns
            painter.setPen(QColor(0, 0, 0))
        # Set font style
        font = QFont()
        font.setBold(True)  # Set font to bold
        font.setPointSize(12)  # Set font size to 12
        painter.setFont(font)

        # Draw cell text centered
        painter.drawText(option.rect, Qt.AlignCenter, index.data())

        painter.restore()


class TaskForm(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("المهام اليومية")
        self.setGeometry(120, 120, 800, 600)
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        self.task_name_label = QLabel("اسم المهمة:")
        self.task_name_entry = QLineEdit()
        self.task_status_label = QLabel("الحالة:")
        self.task_status_dropdown = QComboBox()
        self.task_status_dropdown.addItem("تحت الإجراء")
        self.task_status_dropdown.addItem("غير منجزة")
        self.task_status_dropdown.addItem("أنجزت")
        self.task_desc_label = QLabel("سبب عدم الإنجاز")
        self.task_desc_entry = QLineEdit()
        self.button_layout = QHBoxLayout()
        self.submit_button = HoverButton("إضـــــــافة")
        self.submit_button.clicked.connect(self.submit_form)
        self.submit_button.setStyleSheet(
            "background-color: #2B2A4C; color: white; padding:8px; border:0; border-radius:3px")
        self.update_button = HoverButton("تحديث")
        self.update_button.clicked.connect(self.update_form)
        self.update_button.setStyleSheet(
            "background-color: #EA906C; color: white; padding:8px; border:0; border-radius:3px")
        self.delete_button = HoverButton("حذف")
        self.delete_button.clicked.connect(self.delete_task)
        # Set the background color of the delete button to red
        self.delete_button.setStyleSheet(
            "background-color: #B31312; color:white;padding:8px; border:0; border-radius:3px ")
        self.show_table_button = HoverButton('عرض البيانات')
        # Set the background color of the delete button to red
        self.show_table_button.setStyleSheet(
            "background-color: #9376E0; color:white;padding:8px; border:0; border-radius:3px ")
        self.show_table_button.clicked.connect(self.load_tasks)
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addWidget(self.update_button)
        self.button_layout.addWidget(self.delete_button)
        self.button_layout.addWidget(self.show_table_button)
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["رقم المهمة", "اسم المهمة",
                                             "سبب عدم الإنجاز", "الحالة", "تاريخ إنشاء المهمة"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setSelectionMode(QTableWidget.SingleSelection)
        self.table.itemSelectionChanged.connect(self.load_selected_task)
        self.layout.addWidget(self.task_name_label)
        self.layout.addWidget(self.task_name_entry)
        self.layout.addWidget(self.task_status_label)
        self.layout.addWidget(self.task_status_dropdown)
        self.layout.addWidget(self.task_desc_label)
        self.layout.addWidget(self.task_desc_entry)
        self.layout.addLayout(self.button_layout)
        self.layout.addWidget(self.table)
        self.create_table()

    def check_data(self):
        task_name = self.task_name_entry.text()
        if len(task_name) == 0:
            QMessageBox.critical(self, "خطأ", "لم تدخل بيانات!")
            return False
        return True

    def create_table(self):
        conn = sqlite3.connect('tasks.db')
        curr = conn.cursor()
        create_table_query = '''CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY,
                                name TEXT,
                                description TEXT,
                                status TEXT,
                                date_created TEXT
        )'''
        curr.execute(create_table_query)

    def submit_form(self):
        task_name = self.task_name_entry.text()
        task_status = self.task_status_dropdown.currentText()
        task_desc = self.task_desc_entry.text()
        date_created = QDateTime.currentDateTime().toString(Qt.ISODate)

        if not self.check_data():
            return

        msg_box = QMessageBox.question(self, "تأكيد",
                                       f"اسم المهمة: {task_name}\n\nهل أنت متأكد من إضافة ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if msg_box == QMessageBox.Yes:
            conn = sqlite3.connect("tasks.db")
            c = conn.cursor()
            c.execute("INSERT INTO tasks (name, description, status, date_created) VALUES (?, ?, ?, ?)",
                      (task_name, task_desc, task_status, date_created))
            conn.commit()
            conn.close()
            self.clear_task()
            self.load_tasks()

    def update_form(self):
        select = self.table.selectedItems()
        if not select:
            QMessageBox.critical(self, "خطأ", "لم تختر مهمة!")
            return
        task_id = select[0].text()
        task_name = self.task_name_entry.text()
        task_status = self.task_status_dropdown.currentText()
        task_desc = self.task_desc_entry.text()
        if not self.check_data():
            return

        msg_box = QMessageBox.question(self, "تأكيد",
                                       f"اسم المهمة: {task_name}\n\nهل أنت متأكد من تحديث ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if msg_box == QMessageBox.Yes:
            conn = sqlite3.connect("tasks.db")
            c = conn.cursor()
            c.execute("UPDATE tasks SET name=?, description=?, status=? WHERE id=?",
                      (task_name, task_desc, task_status, task_id))
            conn.commit()
            conn.close()
            self.clear_task()
            self.load_tasks()

    def load_tasks(self):
        conn = sqlite3.connect("tasks.db")
        c = conn.cursor()
        c.execute("SELECT * FROM tasks")
        rows = c.fetchall()
        conn.close()

        self.table.setRowCount(0)
        font = QFont()
        for row in rows:
            self.table.insertRow(self.table.rowCount())
            for i in range(len(row)):
                item = QTableWidgetItem(str(row[i]))
                if i == 3:  # Column index of the status
                    status = str(row[i])
                    if status == "منجزة" or status == 'أنجزت':
                        # Set green background for status 'أنجزت'
                        item.setForeground(QColor('#090580'))
                        font.setBold(True)
                        item.setFont(font)
                    else:
                        # Set red background for other statuses
                        item.setForeground(QColor('#B70404'))
                        item.setFont(font)
                item.setTextAlignment(Qt.AlignCenter)

                self.table.setItem(self.table.rowCount() - 1, i, item)
        self.table.setStyleSheet("""
                QTableWidget QTableCornerButton::section,
                QTableWidget QHeaderView::section,
                QTableWidget{
                    border: 1px solid black;
                }
                QTableWidget::item {
                    border: 1px solid black;
                    padding: 0px;
                }
                QTableWidget::item:selected {
                    background-color: #A9D0F5;  /* Set the background color of the selected row */
                }
            """)
        self.table.resizeColumnsToContents(
        )  # Resize columns automatically based on cell contents
        self.table.setLayoutDirection(Qt.RightToLeft)

    def load_selected_task(self):
        select = self.table.selectedItems()
        if not select:
            # Clear the form fields and return
            self.clear_task()
            return

        task_id = select[0].text()

        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()
        c.execute("SELECT * FROM tasks WHERE id=?", (task_id,))
        row = c.fetchone()
        conn.close()

        self.task_name_entry.setText(row[1] if row else '')
        self.task_desc_entry.setText(row[2] if row else '')
        self.task_status_dropdown.setCurrentText(row[3] if row else '')

    def delete_task(self):
        select = self.table.selectedItems()
        if not select:
            QMessageBox.critical(self, "Error", "No task selected!")
            return
        task_id = select[0].text()
        task_name = select[1].text()

        msg_box = QMessageBox.question(self, "تأكيد",
                                       f"اسم المهمة: {task_name}\n\nهل أنت متأكد من حذف ?",
                                       QMessageBox.Yes | QMessageBox.No)
        if msg_box == QMessageBox.Yes:
            conn = sqlite3.connect("tasks.db")
            c = conn.cursor()
            c.execute("DELETE FROM tasks WHERE id=?", (task_id,))
            conn.commit()
            conn.close()
            self.clear_task()
            self.load_tasks()

    def clear_task(self):
        self.task_name_entry.clear()
        self.task_desc_entry.clear()
        self.task_status_dropdown.setCurrentIndex(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setGeometry(120, 120, 800, 600)
        self.tab_widget = QTabWidget()
        self.user_tab = User()
        self.task_tab = TaskForm()
        self.employee_tab = EmployeeTrackerGUI()
        self.tab_widget.addTab(self.task_tab, "المهام اليومية")
        self.tab_widget.addTab(self.employee_tab, "الحضور والانصراف")        
        self.tab_widget.addTab(self.user_tab,'المستخدم')


        self.setCentralWidget(self.tab_widget)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    task_form = MainWindow()
    task_form.show()
    sys.exit(app.exec_())
