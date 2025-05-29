import os
import sys
import random
import math

from PyQt5.QtWidgets import (
    QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QFrame,
    QGraphicsDropShadowEffect, QApplication
)
from PyQt5.QtCore import Qt, QPointF, QTimer
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush

# تعديل المسارات للاستيراد
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
import db_manager

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'admin')))
from inventory_view import InventoryView
from manage_products import ManageProductsWindow
from sales_report import SalesReportWindow  # تأكد أن الملف موجود

class MovingShape:
    def __init__(self, x, y, size, dx, dy):
        self.x = x
        self.y = y
        self.size = size
        self.dx = dx
        self.dy = dy
        self.current_hue = random.uniform(180, 240)
        self.target_hue = self.current_hue

    def move(self, width, height, mouse_pos):
        dx_mouse = self.x - mouse_pos.x()
        dy_mouse = self.y - mouse_pos.y()
        dist = math.sqrt(dx_mouse * dx_mouse + dy_mouse * dy_mouse)
        if dist < 150 and dist != 0:
            factor = (150 - dist) / 150 * 3
            self.dx += (dx_mouse / dist) * factor
            self.dy += (dy_mouse / dist) * factor
            self.target_hue = 160
        else:
            self.dx *= 0.95
            self.dy *= 0.95
            self.target_hue = 210

        diff = self.target_hue - self.current_hue
        self.current_hue += diff * 0.1

        self.x += self.dx
        self.y += self.dy

        if self.x < 0:
            self.x = 0
            self.dx *= -1
        elif self.x > width:
            self.x = width
            self.dx *= -1

        if self.y < 0:
            self.y = 0
            self.dy *= -1
        elif self.y > height:
            self.y = height
            self.dy *= -1

class Card(QFrame):
    def __init__(self, title, icon, parent=None):
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet("""
            QFrame#card {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
            }
            QLabel {
                color: white;
            }
        """)
        self.setGraphicsEffect(self.create_shadow())

        self.title_label = QLabel(f"{icon} {title}")
        self.title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        self.value_label = QLabel("...")  # سيتم التحديث من قاعدة البيانات
        self.value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

    def create_shadow(self):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setOffset(0, 0)
        shadow.setColor(QColor(0, 0, 0, 160))
        return shadow

    def set_value(self, text):
        self.value_label.setText(text)

class AdminHome(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("لوحة تحكم الأدمن")
        self.showFullScreen()
        self.setMouseTracking(True)

        self.shapes = [self.create_random_shape() for _ in range(30)]
        self.mouse_pos = QPointF(self.width() / 2, self.height() / 2)

        self.init_ui()
        self.load_data()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(30)

        self.data_timer = QTimer()
        self.data_timer.timeout.connect(self.load_data)
        self.data_timer.start(5000)  # تحديث البيانات كل 5 ثوانٍ

        # النوافذ الفرعية
        self.inventory_window = None
        self.manage_products_window = None
        self.sales_report_window = None

    def create_random_shape(self):
        x = random.randint(0, max(1, self.width()))
        y = random.randint(0, max(1, self.height()))
        size = random.randint(15, 30)
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        return MovingShape(x, y, size, dx, dy)

    def init_ui(self):
        self.setStyleSheet("""
            QPushButton {
                background-color: #00796b;
                color: white;
                padding: 14px 24px;
                font-size: 18px;
                border-radius: 12px;
                font-weight: bold;
                min-width: 160px;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
            QLabel#titleLabel {
                color: white;
                font-size: 42px;
                font-weight: bold;
                qproperty-alignment: AlignCenter;
            }
            QFrame#card {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 15px;
            }
            QLabel {
                color: white;
            }
        """)

        # الأزرار
        self.btn_manage_products = QPushButton("📦 إدارة المنتجات")
        self.btn_manage_users = QPushButton("👥 إدارة المستخدمين")
        self.btn_inventory = QPushButton("📋 عرض المخزون")
        self.btn_sales_report = QPushButton("📊 تقرير المبيعات")
        self.btn_activity_log = QPushButton("🕒 سجل الأنشطة")
        self.btn_settings = QPushButton("🔧 الإعدادات")
        self.btn_backup = QPushButton("🗂️ نسخ احتياطي / استعادة")

        # ربط الأزرار
        self.btn_manage_products.clicked.connect(self.open_manage_products_window)
        self.btn_manage_users.clicked.connect(lambda: print("فتح إدارة المستخدمين"))
        self.btn_inventory.clicked.connect(self.open_inventory_window)
        self.btn_sales_report.clicked.connect(self.open_sales_report_window)
        self.btn_activity_log.clicked.connect(lambda: print("فتح سجل الأنشطة"))
        self.btn_settings.clicked.connect(lambda: print("فتح الإعدادات"))
        self.btn_backup.clicked.connect(lambda: print("فتح النسخ الاحتياطي"))

        # بطاقات عرض البيانات
        self.card_products = Card("عدد المنتجات", "📦")
        self.card_users = Card("عدد المستخدمين", "👥")

        # تخطيط الأزرار
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.btn_manage_products)
        buttons_layout.addWidget(self.btn_manage_users)
        buttons_layout.addWidget(self.btn_inventory)
        buttons_layout.addWidget(self.btn_sales_report)
        buttons_layout.addWidget(self.btn_activity_log)
        buttons_layout.addWidget(self.btn_settings)
        buttons_layout.addWidget(self.btn_backup)

        # تخطيط البطاقات
        cards_layout = QHBoxLayout()
        cards_layout.addWidget(self.card_products)
        cards_layout.addWidget(self.card_users)

        main_layout = QVBoxLayout()
        self.title_label = QLabel("لوحة تحكم الأدمن")
        self.title_label.setObjectName("titleLabel")
        main_layout.addWidget(self.title_label)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(cards_layout)
        main_layout.addStretch()

        self.setLayout(main_layout)

    def load_data(self):
        # جلب عدد المنتجات وعدد المستخدمين من قاعدة البيانات
        try:
            products_count = db_manager.get_products_count()
            users_count = db_manager.get_users_count()
            self.card_products.set_value(str(products_count))
            self.card_users.set_value(str(users_count))
        except Exception as e:
            print(f"Error loading data: {e}")

    def open_inventory_window(self):
        if self.inventory_window is None:
            self.inventory_window = InventoryView()
        self.inventory_window.show()
        self.inventory_window.raise_()
        self.inventory_window.activateWindow()

    def open_manage_products_window(self):
        if self.manage_products_window is None:
            self.manage_products_window = ManageProductsWindow()
        self.manage_products_window.show()
        self.manage_products_window.raise_()
        self.manage_products_window.activateWindow()

    def open_sales_report_window(self):
        if self.sales_report_window is None:
            self.sales_report_window = SalesReportWindow()
        self.sales_report_window.show()
        self.sales_report_window.raise_()
        self.sales_report_window.activateWindow()

    def update_scene(self):
        self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.localPos()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(33, 150, 243))
        gradient.setColorAt(1, QColor(13, 71, 161))
        painter.fillRect(self.rect(), QBrush(gradient))

        for shape in self.shapes:
            shape.move(self.width(), self.height(), self.mouse_pos)
            color = QColor.fromHsvF(shape.current_hue / 360, 1, 1)
            painter.setBrush(color)
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(int(shape.x), int(shape.y), shape.size, shape.size)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdminHome()
    window.show()
    sys.exit(app.exec_())
