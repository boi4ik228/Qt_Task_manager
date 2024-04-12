import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLineEdit, QListWidget, QInputDialog, QDateEdit
from PyQt5.QtCore import QDate

def create_connection(db_file):
    conn = sqlite3.connect(db_file)
    return conn

def create_task(conn, task):
    sql = ''' INSERT INTO tasks(title, description, status, date)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()
    return cur.lastrowid

def select_all_tasks(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
    rows = cur.fetchall()
    return rows

def update_task(conn, task):
    sql = ''' UPDATE tasks
              SET title = ?,
                  description = ?,
                  status = ?,
                  date = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, task)
    conn.commit()

def delete_task(conn, id):
    sql = 'DELETE FROM tasks WHERE id=?'
    cur = conn.cursor()
    cur.execute(sql, (id,))
    conn.commit()

class MyWindow(QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Менеджер Задач")
        self.setGeometry(200, 200, 600, 400)

        layout = QVBoxLayout()

        self.listWidget = QListWidget()
        self.loadTasks()

        self.lineEdit = QLineEdit()
        self.dateEdit = QDateEdit()
        self.dateEdit.setDate(QDate.currentDate())

        self.addButton = QPushButton("Добавить Задачу")
        self.addButton.clicked.connect(self.addTask)

        self.deleteButton = QPushButton("Удалить Задачу")
        self.deleteButton.clicked.connect(self.deleteTask)

        self.completeButton = QPushButton("Задача Выполнена")
        self.completeButton.clicked.connect(self.completeTask)

        self.editButton = QPushButton("Изменить Задачу")
        self.editButton.clicked.connect(self.editTask)

        layout.addWidget(self.listWidget)
        layout.addWidget(self.lineEdit)
        layout.addWidget(self.dateEdit)
        layout.addWidget(self.addButton)
        layout.addWidget(self.deleteButton)
        layout.addWidget(self.completeButton)
        layout.addWidget(self.editButton)

        container = QWidget()
        container.setLayout(layout)

        self.setCentralWidget(container)

    def loadTasks(self):
        self.listWidget.clear()
        conn = create_connection("tasks.db")
        tasks = select_all_tasks(conn)
        for task in tasks:
            status = "Выполнено" if task[3] else "В процессе"
            self.listWidget.addItem(f"{task[0]}: {task[1]} [Статус: {status}, Дата: {task[4]}]")

    def addTask(self):
        task_title = self.lineEdit.text()
        task_date = self.dateEdit.date().toString("yyyy-MM-dd")
        if task_title:
            conn = create_connection("tasks.db")
            create_task(conn, (task_title, '', 0, task_date))
            self.lineEdit.clear()
            self.loadTasks()

    def deleteTask(self):
        selected_item = self.listWidget.currentItem()
        if selected_item:
            task_id = selected_item.text().split(":")[0]
            conn = create_connection("tasks.db")
            delete_task(conn, task_id)
            self.loadTasks()

    def completeTask(self):
        selected_item = self.listWidget.currentItem()
        if selected_item:
            task_id = selected_item.text().split(":")[0]
            conn = create_connection("tasks.db")
            update_task(conn, ('', '', 1, '', task_id))
            self.loadTasks()

    def editTask(self):
        selected_item = self.listWidget.currentItem()
        if selected_item:
            task_id = int(selected_item.text().split(":")[0])
            text, ok = QInputDialog.getText(self, 'Изменить Задачу', 'Введите новое название задачи:')
            if ok and text:
                conn = create_connection("tasks.db")
                update_task(conn, (text, '', 0, '', task_id))
                self.loadTasks()

def main():
    conn = create_connection("tasks.db")
    sql_create_tasks_table = """ CREATE TABLE IF NOT EXISTS tasks (
                                        id integer PRIMARY KEY,
                                        title text NOT NULL,
                                        description text,
                                        status integer NOT NULL,
                                        date text NOT NULL
                                    ); """
    c = conn.cursor()
    c.execute(sql_create_tasks_table)
    conn.commit()
    conn.close()

    app = QApplication(sys.argv)
    mainWin = MyWindow()
    mainWin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
