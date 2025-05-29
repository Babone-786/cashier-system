import sys
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QSpinBox,
    QMessageBox, QComboBox
)
from PyQt5.QtCore import Qt

# استيراد مكتبات الطباعة لو متوفرة
try:
    import win32print
    import win32api
    WINDOWS_PRINT = True
except ImportError:
    WINDOWS_PRINT = False

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from db_manager import get_all_products, add_sale

class SalesPage(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("صفحة البيع - كاشير")
        self.setGeometry(100, 100, 1000, 650)
        self.init_ui()
        self.load_products()

    def init_ui(self):
        layout = QVBoxLayout()

        title = QLabel("📋 صفحة البيع")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        layout.addWidget(title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["معرف المنتج", "اسم المنتج", "السعر", "المخزون", "الكمية للبيع"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        # اختيار نوع الدفع
        payment_layout = QHBoxLayout()
        payment_label = QLabel("نوع الدفع:")
        payment_label.setStyleSheet("font-size: 16px;")
        self.payment_combo = QComboBox()
        self.payment_combo.addItems(["كاش", "بنك", "فوري"])
        self.payment_combo.setStyleSheet("font-size: 16px;")
        payment_layout.addWidget(payment_label)
        payment_layout.addWidget(self.payment_combo)
        payment_layout.addStretch()
        layout.addLayout(payment_layout)

        # أزرار البيع والطباعة والإغلاق
        btn_layout = QHBoxLayout()

        self.print_button = QPushButton("طباعة الفاتورة")
        self.print_button.clicked.connect(self.print_invoice)
        btn_layout.addWidget(self.print_button)

        self.sell_button = QPushButton("تأكيد البيع")
        self.sell_button.clicked.connect(self.sell_products)
        btn_layout.addWidget(self.sell_button)

        self.close_button = QPushButton("إغلاق")
        self.close_button.clicked.connect(self.close)  # إغلاق النافذة عند الضغط
        btn_layout.addWidget(self.close_button)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def load_products(self):
        all_products = get_all_products()
        products_in_stock = [p for p in all_products if p[3] > 0]

        self.table.setRowCount(len(products_in_stock))

        for row, product in enumerate(products_in_stock):
            product_id, name, price, quantity = product

            self.table.setItem(row, 0, QTableWidgetItem(str(product_id)))
            self.table.setItem(row, 1, QTableWidgetItem(name))
            self.table.setItem(row, 2, QTableWidgetItem(f"{price:.2f}"))
            self.table.setItem(row, 3, QTableWidgetItem(str(quantity)))

            spin = QSpinBox()
            spin.setRange(0, quantity)
            spin.setValue(0)
            self.table.setCellWidget(row, 4, spin)

    def collect_sales(self):
        sales = []
        for row in range(self.table.rowCount()):
            product_id = int(self.table.item(row, 0).text())
            name = self.table.item(row, 1).text()
            price = float(self.table.item(row, 2).text())
            quantity_in_stock = int(self.table.item(row, 3).text())
            spin: QSpinBox = self.table.cellWidget(row, 4)
            quantity_to_sell = spin.value()
            if quantity_to_sell > 0 and quantity_to_sell <= quantity_in_stock:
                sales.append({
                    "product_id": product_id,
                    "name": name,
                    "price": price,
                    "quantity": quantity_to_sell,
                    "total": price * quantity_to_sell
                })
        return sales

    def print_invoice(self):
        sales = self.collect_sales()
        if not sales:
            QMessageBox.warning(self, "تحذير", "لم يتم تحديد أي منتج للبيع للطباعة.")
            return

        payment_method = self.payment_combo.currentText()
        total_amount = sum(item['total'] for item in sales)

        invoice_text = "----- فاتورة البيع -----\n"
        for item in sales:
            invoice_text += f"{item['name']} - {item['quantity']} × {item['price']:.2f} = {item['total']:.2f}\n"
        invoice_text += f"\nالمجموع: {total_amount:.2f}\n"
        invoice_text += f"طريقة الدفع: {payment_method}\n"
        invoice_text += "------------------------\n"
        invoice_text += "شكراً لتعاملكم معنا!"

        if WINDOWS_PRINT:
            try:
                printer_name = win32print.GetDefaultPrinter()
                hPrinter = win32print.OpenPrinter(printer_name)
                try:
                    hDC = win32print.StartDocPrinter(hPrinter, 1, ("فاتورة", None, "RAW"))
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, invoice_text.encode('utf-8'))
                    win32print.EndPagePrinter(hPrinter)
                    win32print.EndDocPrinter(hPrinter)
                    QMessageBox.information(self, "طباعة", "تم إرسال الفاتورة للطابعة بنجاح.")
                finally:
                    win32print.ClosePrinter(hPrinter)
            except Exception as e:
                QMessageBox.warning(self, "خطأ طباعة", f"حدث خطأ أثناء الطباعة:\n{e}")
        else:
            try:
                with open("فاتورة_البيع.txt", "w", encoding="utf-8") as f:
                    f.write(invoice_text)
                QMessageBox.information(self, "طباعة بديلة",
                    "مكتبة الطباعة غير متوفرة.\nتم حفظ الفاتورة في 'فاتورة_البيع.txt'.\nيرجى طباعتها يدوياً.")
            except Exception as e:
                QMessageBox.warning(self, "خطأ", f"تعذر حفظ الفاتورة:\n{e}")

    def sell_products(self):
        sales = self.collect_sales()
        if not sales:
            QMessageBox.information(self, "تنبيه", "لم يتم اختيار أي كمية للبيع.")
            return

        errors = []
        for item in sales:
            try:
                add_sale(item["product_id"], item["quantity"], item["total"])
            except Exception as e:
                errors.append(f"خطأ في بيع المنتج {item['name']}: {e}")

        if errors:
            QMessageBox.warning(self, "أخطاء", "\n".join(errors))
        else:
            QMessageBox.information(self, "نجاح", "تمت عملية البيع بنجاح!")
            self.load_products()
            for row in range(self.table.rowCount()):
                spin: QSpinBox = self.table.cellWidget(row, 4)
                spin.setValue(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SalesPage()
    window.show()
    sys.exit(app.exec_())
