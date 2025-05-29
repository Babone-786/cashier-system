import sys
import subprocess
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout
)
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush
from PyQt5.QtCore import Qt, QTimer, QPointF
import random

from inventory_page import InventoryPage  # ✅ الاسم الجديد للملف والصفحة
from sales_page import SalesPage  # ✅ إضافة استيراد صفحة البيع

class MovingShape:
    def __init__(self, x, y, size, dx, dy):
        self.x = x
        self.y = y
        self.size = size
        self.dx = dx
        self.dy = dy
        self.current_hue = random.uniform(180, 240)
        self.target_hue = self.current_hue

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x < 0 or self.x > width:
            self.dx *= -1
        if self.y < 0 or self.y > height:
            self.dy *= -1
        diff = self.target_hue - self.current_hue
        self.current_hue += diff * 0.05

class CashierWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("كاشير")
        self.showFullScreen()

        self.shapes = [self.create_random_shape() for _ in range(25)]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(40)

        self.init_ui()

    def create_random_shape(self):
        x = random.randint(0, self.width())
        y = random.randint(0, self.height())
        size = random.randint(12, 26)
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        return MovingShape(x, y, size, dx, dy)

    def init_ui(self):
        self.setStyleSheet("""
            QPushButton {
                padding: 15px;
                background-color: #00796b;
                color: white;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
            QLabel {
                color: white;
                font-size: 22px;
                font-weight: bold;
            }
        """)

        title = QLabel("📊 لوحة كاشير")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Segoe UI", 32, QFont.Bold))

        stats = QGridLayout()
        stats.addWidget(QLabel("📦 عدد المنتجات في المخزن: 120"), 0, 0)
        stats.addWidget(QLabel("🛒 المبيعات اليوم: 35000 SDG"), 1, 0)

        buttons = QHBoxLayout()
        sell_product_btn = QPushButton("🔄 بيع منتج")
        sell_product_btn.clicked.connect(self.show_sales_page)  # ربط الزر بفتح صفحة البيع
        buttons.addWidget(sell_product_btn)

        view_inventory_btn = QPushButton("📦 عرض المخزون")
        view_inventory_btn.clicked.connect(self.show_inventory_page)
        buttons.addWidget(view_inventory_btn)

        sales_report_btn = QPushButton("📈 تقرير المبيعات")
        sales_report_btn.clicked.connect(self.open_sales_report)
        buttons.addWidget(sales_report_btn)

        layout = QVBoxLayout()
        layout.addSpacing(40)
        layout.addWidget(title)
        layout.addSpacing(30)
        layout.addLayout(stats)
        layout.addSpacing(20)
        layout.addLayout(buttons)
        layout.addStretch()
        layout.setContentsMargins(300, 100, 300, 100)
        self.setLayout(layout)

    def show_sales_page(self):
        self.sales_window = SalesPage()
        self.sales_window.showFullScreen()

    def show_inventory_page(self):
        self.inventory_window = InventoryPage()
        self.inventory_window.showFullScreen()

    def open_sales_report(self):
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sales_report.py")
        subprocess.Popen([sys.executable, script_path], creationflags=subprocess.CREATE_NEW_CONSOLE)

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(0, 102, 204))
        gradient.setColorAt(1, QColor(0, 204, 255))
        painter.fillRect(self.rect(), QBrush(gradient))

        painter.setRenderHint(QPainter.Antialiasing)
        for shape in self.shapes:
            color = QColor()
            color.setHsvF(shape.current_hue / 360.0, 1.0, 1.0, 0.8)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(shape.x, shape.y), shape.size, shape.size)

    def update_scene(self):
        for shape in self.shapes:
            shape.move(self.width(), self.height())
        self.update()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = CashierWindow()
    win.show()
    sys.exit(app.exec_())
