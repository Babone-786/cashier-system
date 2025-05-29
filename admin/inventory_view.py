import sys
import os

# أضف مسار مجلد database إلى sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))

import db_manager  # الآن بايثون يقدر يلقا الملف db_manager.py

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QApplication

class InventoryView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("عرض المخزون")
        self.resize(600, 400)

        self.layout = QVBoxLayout()
        self.table = QTableWidget()
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.load_products()

    def load_products(self):
        products = db_manager.get_all_products()
        self.table.setRowCount(len(products))
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "اسم المنتج", "السعر", "الكمية"])

        for row_idx, product in enumerate(products):
            self.table.setItem(row_idx, 0, QTableWidgetItem(str(product[0])))  # id
            self.table.setItem(row_idx, 1, QTableWidgetItem(product[1]))       # name
            self.table.setItem(row_idx, 2, QTableWidgetItem(str(product[2])))  # price
            self.table.setItem(row_idx, 3, QTableWidgetItem(str(product[3])))  # quantity

if __name__ == "__main__":
    # تأكد من وجود الجداول في قاعدة البيانات
    db_manager.create_tables()

    app = QApplication(sys.argv)
    window = InventoryView()
    window.show()
    sys.exit(app.exec_())
