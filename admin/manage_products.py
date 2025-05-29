import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QApplication,
    QDialog, QLineEdit, QFormLayout, QMessageBox
)
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QBrush
from PyQt5.QtCore import Qt

# إعداد المسارات
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
database_dir = os.path.join(parent_dir, 'database')
admin_dir = os.path.join(parent_dir, 'admin')

if database_dir not in sys.path:
    sys.path.insert(0, database_dir)
if admin_dir not in sys.path:
    sys.path.insert(0, admin_dir)

import db_manager



class AddProductDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة منتج جديد")
        self.setFixedSize(400, 250)

        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel, QLineEdit, QPushButton {
                color: #000000;
                font-size: 16px;
            }
            QPushButton {
                background-color: #00796b;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
        """)

        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.price_input = QLineEdit()
        self.quantity_input = QLineEdit()

        layout.addRow("اسم المنتج:", self.name_input)
        layout.addRow("السعر:", self.price_input)
        layout.addRow("الكمية:", self.quantity_input)

        self.btn_add = QPushButton("إضافة")
        self.btn_add.clicked.connect(self.add_product)
        layout.addWidget(self.btn_add)

        self.setLayout(layout)

    def add_product(self):
        name = self.name_input.text().strip()
        try:
            price = float(self.price_input.text().strip())
            quantity = int(self.quantity_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "خطأ", "تأكد من أن السعر والكمية أرقام صحيحة.")
            return

        if not name:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المنتج.")
            return

        try:
            db_manager.add_product(name, price, quantity)
            QMessageBox.information(self, "تم", "تمت إضافة المنتج بنجاح.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الإضافة: {e}")


class EditProductDialog(QDialog):
    def __init__(self, prod_id, name, price, quantity, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تعديل المنتج")
        self.setFixedSize(400, 250)
        self.prod_id = prod_id

        self.setStyleSheet("""
            QDialog {
                background-color: #ffffff;
            }
            QLabel, QLineEdit, QPushButton {
                color: #000000;
                font-size: 16px;
            }
            QPushButton {
                background-color: #00796b;
                color: white;
                padding: 10px 20px;
                border-radius: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
        """)

        layout = QFormLayout()

        self.name_input = QLineEdit(name)
        self.price_input = QLineEdit(str(price))
        self.quantity_input = QLineEdit(str(quantity))

        layout.addRow("اسم المنتج:", self.name_input)
        layout.addRow("السعر:", self.price_input)
        layout.addRow("الكمية:", self.quantity_input)

        self.btn_update = QPushButton("تحديث")
        self.btn_update.clicked.connect(self.update_product)
        layout.addWidget(self.btn_update)

        self.setLayout(layout)

    def update_product(self):
        name = self.name_input.text().strip()
        try:
            price = float(self.price_input.text().strip())
            quantity = int(self.quantity_input.text().strip())
        except ValueError:
            QMessageBox.warning(self, "خطأ", "تأكد من أن السعر والكمية أرقام صحيحة.")
            return

        if not name:
            QMessageBox.warning(self, "تنبيه", "يرجى إدخال اسم المنتج.")
            return

        try:
            db_manager.update_product(self.prod_id, name, price, quantity)
            QMessageBox.information(self, "تم", "تم تحديث المنتج بنجاح.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء التحديث: {e}")


class ManageProductsWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("إدارة المنتجات")
        self.resize(920, 640)
        self.setMouseTracking(True)

        self.init_ui()
        self.load_products()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: transparent;
            }
            QLabel#titleLabel {
                font-size: 32px;
                font-weight: bold;
                color: white;
            }
            QPushButton {
                padding: 14px 28px;
                background-color: #00796b;
                color: white;
                border-radius: 14px;
                font-size: 18px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 12px;
                font-size: 18px;
                gridline-color: #00796b;
            }
            QHeaderView::section {
                background-color: #004d40;
                color: white;
                font-weight: bold;
                font-size: 18px;
                height: 35px;
            }
            QTableWidget::item:selected {
                background-color: #00796b;
                color: white;
            }
            QLineEdit {
                padding: 8px;
                font-size: 16px;
                border-radius: 10px;
                border: 2px solid #00796b;
                background-color: white;
                min-width: 240px;
            }
        """)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(30, 30, 30, 30)
        self.setLayout(self.layout)

        self.title = QLabel("إدارة المنتجات")
        self.title.setObjectName("titleLabel")
        self.title.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.title)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث باسم المنتج...")
        self.btn_search = QPushButton("بحث")
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        self.layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "اسم المنتج", "السعر", "الكمية"])
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)
        self.layout.addWidget(self.table)

        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("إضافة منتج")
        self.btn_edit = QPushButton("تعديل المنتج")
        self.btn_delete = QPushButton("حذف المنتج")
        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        self.layout.addLayout(btn_layout)

        self.btn_add.clicked.connect(self.show_add_dialog)
        self.btn_edit.clicked.connect(self.show_edit_dialog)
        self.btn_delete.clicked.connect(self.delete_product)
        self.btn_search.clicked.connect(self.search_products)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, QColor(5, 87, 77))
        gradient.setColorAt(1, QColor(5, 125, 110))
        painter.fillRect(self.rect(), QBrush(gradient))
        super().paintEvent(event)

    def load_products(self, filter_text=""):
        self.table.setRowCount(0)
        products = db_manager.get_all_products()

        for prod in products:
            prod_id, name, price, quantity = prod
            if filter_text and filter_text.lower() not in name.lower():
                continue
            row_num = self.table.rowCount()
            self.table.insertRow(row_num)
            self.table.setItem(row_num, 0, QTableWidgetItem(str(prod_id)))
            self.table.setItem(row_num, 1, QTableWidgetItem(name))
            self.table.setItem(row_num, 2, QTableWidgetItem(f"{price:.2f}"))
            self.table.setItem(row_num, 3, QTableWidgetItem(str(quantity)))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def search_products(self):
        text = self.search_input.text().strip()
        self.load_products(filter_text=text)

    def show_add_dialog(self):
        dialog = AddProductDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_products()

    def show_edit_dialog(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            msg = QMessageBox(self)
            msg.setWindowTitle("تنبيه")
            msg.setText("يرجى اختيار منتج لتعديله.")
            msg.setStyleSheet("QLabel{color: white; font-size: 14pt;} QPushButton{min-width: 80px; font-size: 12pt;}")
            msg.exec()
            return

        row = selected_rows[0].row()
        prod_id = int(self.table.item(row, 0).text())
        name = self.table.item(row, 1).text()
        price = float(self.table.item(row, 2).text())
        quantity = int(self.table.item(row, 3).text())

        dialog = EditProductDialog(prod_id, name, price, quantity, self)
        if dialog.exec() == QDialog.Accepted:
            self.load_products()

    def delete_product(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "تنبيه", "يرجى اختيار منتج للحذف.")
            return

        reply = QMessageBox.question(self, "تأكيد الحذف",
                                     "هل أنت متأكد من حذف المنتج؟",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            row = selected_rows[0].row()
            prod_id = int(self.table.item(row, 0).text())
            try:
                db_manager.delete_product(prod_id)
                QMessageBox.information(self, "نجاح", "تم حذف المنتج بنجاح.")
                self.load_products()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء الحذف: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMessageBox {
            background-color: white;
        }
        QLabel {
            color: white;
        }
        QPushButton {
            background-color: #00796b;
            color: white;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #004d40;
        }
    """)
    window = ManageProductsWindow()
    window.show()
    sys.exit(app.exec())
