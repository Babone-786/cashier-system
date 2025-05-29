import sys
import os
from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QHBoxLayout, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt
from datetime import datetime, timedelta

# إضافة مسار مجلد قاعدة البيانات للاستيراد الصحيح
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from db_manager import get_sales

class SalesReportWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تقرير المبيعات")
        self.resize(800, 600)

        main_layout = QVBoxLayout()

        # العنوان الرئيسي
        title = QLabel("تقرير المبيعات")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        main_layout.addWidget(title)

        # فلاتر التاريخ (اليوم، الأسبوع، الشهر، الكل)
        filter_layout = QHBoxLayout()
        self.filter_group = QButtonGroup(self)
        self.radio_today = QRadioButton("اليوم")
        self.radio_week = QRadioButton("الأسبوع")
        self.radio_month = QRadioButton("الشهر")
        self.radio_all = QRadioButton("الكل")
        self.radio_all.setChecked(True)

        for i, rb in enumerate([self.radio_today, self.radio_week, self.radio_month, self.radio_all]):
            self.filter_group.addButton(rb, i)
            filter_layout.addWidget(rb)

        main_layout.addLayout(filter_layout)

        # جدول عرض المبيعات
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["رقم العملية", "معرف المنتج", "الكمية", "المبلغ", "التاريخ"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        main_layout.addWidget(self.table)

        # شريط الحالة
        self.status_label = QLabel()
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

        # ربط إشارة تغيير الفلتر بتحميل البيانات
        self.filter_group.buttonClicked.connect(self.load_data)

        self.load_data()

    def load_data(self):
        filter_id = self.filter_group.checkedId()
        filter_map = {
            0: "today",
            1: "week",
            2: "month",
            3: "all"
        }
        filter_type = filter_map.get(filter_id, "all")

        all_sales = get_sales()
        today = datetime.now()
        filtered_sales = []

        if filter_type == "today":
            filtered_sales = [s for s in all_sales if s[4] == today.strftime("%Y-%m-%d")]
        elif filter_type == "week":
            week_ago = today - timedelta(days=7)
            filtered_sales = [s for s in all_sales if week_ago.strftime("%Y-%m-%d") <= s[4] <= today.strftime("%Y-%m-%d")]
        elif filter_type == "month":
            month_ago = today - timedelta(days=30)
            filtered_sales = [s for s in all_sales if month_ago.strftime("%Y-%m-%d") <= s[4] <= today.strftime("%Y-%m-%d")]
        else:
            filtered_sales = all_sales

        self.table.setRowCount(len(filtered_sales))
        for row, sale in enumerate(filtered_sales):
            for col, val in enumerate(sale):
                item = QTableWidgetItem(str(val))
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(row, col, item)

        self.status_label.setText(f"عدد العمليات المعروضة: {len(filtered_sales)}")

# للتشغيل المباشر للاختبار فقط
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    window = SalesReportWindow()
    window.show()
    sys.exit(app.exec_())
