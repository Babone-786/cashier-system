from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import sys
import os

# إضافة مسار قاعدة البيانات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from db_manager import get_all_products

class InventoryPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("عرض المخزون")
        self.setGeometry(100, 100, 900, 600)
        self.setStyleSheet("background-color: #f0f0f0;")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "اسم المنتج", "السعر", "الكمية"])
        self.table.setStyleSheet("font-size: 14px;")
        self.table.setSelectionBehavior(self.table.SelectRows)
        layout.addWidget(self.table)

        refresh_button = QPushButton("🔄 تحديث القائمة")
        refresh_button.setStyleSheet("background-color: #2980b9; color: white; font-size: 16px; padding: 10px;")
        refresh_button.clicked.connect(self.load_data)

        back_button = QPushButton("🔙 رجوع إلى الكاشير")
        back_button.setStyleSheet("background-color: #7f8c8d; color: white; font-size: 16px; padding: 10px;")
        back_button.clicked.connect(self.go_back)

        layout.addWidget(refresh_button)
        layout.addWidget(back_button)

        self.setLayout(layout)
        self.load_data()

    def load_data(self):
        self.table.setRowCount(0)
        products = get_all_products()
        for row_num, row_data in enumerate(products):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def go_back(self):
        self.close()  # فقط يغلق الصفحة ويرجع المستخدم لواجهة الكاشير المفتوحة سابقًا
