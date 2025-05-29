import os
import sys

# إضافة مسار مجلد database إلى sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QMessageBox, QGraphicsOpacityEffect
)
from PyQt5.QtGui import QFont, QPainter, QColor, QLinearGradient, QBrush, QPixmap
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, QPointF

import random
import math

import db_manager  # الآن يمكن استيراده بدون مشاكل

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
        if dist < 150:
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

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - نظام الكاشير")
        self.showFullScreen()
        self.setMouseTracking(True)

        self.shapes = [self.create_random_shape() for _ in range(30)]
        self.mouse_pos = QPointF(self.width() / 2, self.height() / 2)

        self.init_ui()
        self.apply_animation()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_scene)
        self.timer.start(30)

    def create_random_shape(self):
        x = random.randint(0, self.width())
        y = random.randint(0, self.height())
        size = random.randint(12, 28)
        dx = random.uniform(-1, 1)
        dy = random.uniform(-1, 1)
        return MovingShape(x, y, size, dx, dy)

    def init_ui(self):
        self.setStyleSheet("""
            QLineEdit {
                padding: 15px;
                border: 2px solid #0097a7;
                border-radius: 10px;
                font-size: 18px;
                background: rgba(255,255,255,0.85);
            }
            QPushButton {
                padding: 15px;
                background-color: #00796b;
                color: white;
                border: none;
                border-radius: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: #004d40;
            }
        """)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "auth", "logo.png")

        self.logo_label = QLabel()
        pixmap = QPixmap(logo_path)
        self.logo_label.setPixmap(pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.title = QLabel("👨‍💼 تسجيل الدخول")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.title.setStyleSheet("color: white;")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.clicked.connect(self.handle_login)

        self.exit_button = QPushButton("⏹ خروج")
        self.exit_button.clicked.connect(self.close)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.logo_label)
        layout.addWidget(self.title)
        layout.addSpacing(20)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addSpacing(15)
        layout.addWidget(self.login_button)
        layout.addSpacing(10)
        layout.addWidget(self.exit_button)
        layout.addStretch()
        layout.setContentsMargins(500, 100, 500, 100)
        self.setLayout(layout)

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
            shape.move(self.width(), self.height(), self.mouse_pos)
        self.update()

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()

    def handle_login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        role = db_manager.check_user(username, password)
        if role == "admin":
            QMessageBox.information(self, "تم", "مرحباً بك أيها الأدمن!")
            # هنا ممكن تفتح واجهة الأدمن
        elif role == "cashier":
            QMessageBox.information(self, "تم", "مرحباً بك أيها الكاشير!")
            # هنا ممكن تفتح واجهة الكاشير
        else:
            QMessageBox.warning(self, "خطأ", "بيانات الدخول غير صحيحة")

    def apply_animation(self):
        self.effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.effect)

        self.anim = QPropertyAnimation(self.effect, b"opacity")
        self.anim.setDuration(1000)
        self.anim.setStartValue(0)
        self.anim.setEndValue(1)
        self.anim.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim.start()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
