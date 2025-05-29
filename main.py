import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# إضافة المسارات المطلوبة للوصول إلى الموديولات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'database')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'cashier')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'admin')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'auth')))

# استيراد النوافذ
from auth import LoginWindow
from cashier import CashierWindow
from admin import AdminHome

class MainApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.login_window = LoginWindow()
        self.cashier_window = None
        self.admin_window = None

        # ربط حدث تسجيل الدخول
        self.login_window.login_successful.connect(self.open_window_by_role)

    def open_window_by_role(self, role):
        self.login_window.hide()

        if role == "cashier":
            self.cashier_window = CashierWindow()
            self.cashier_window.show()
        elif role == "admin":
            self.admin_window = AdminHome()
            self.admin_window.show()
        else:
            print(f"⚠️ دور غير معروف: {role}")

    def run(self):
        self.login_window.show()
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    main_app = MainApp()
    main_app.run()
