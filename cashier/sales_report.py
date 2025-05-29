import sys
import os
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

# إضافة مسار مجلد قاعدة البيانات
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database')))
from db_manager import get_sales, get_all_products  # استيراد الدوال المطلوبة

class SalesReportWindow(tk.Toplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("تقرير المبيعات - الكاشير")
        self.geometry("850x600")
        self.configure(bg="#f9f9f9")
        self.resizable(False, False)

        # تحميل بيانات المنتجات في dict {id: name}
        self.products_dict = {prod[0]: prod[1] for prod in get_all_products()}

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # عنوان الصفحة
        title_label = tk.Label(self, text="تقرير المبيعات", font=("Arial", 18, "bold"), bg="#f9f9f9")
        title_label.pack(pady=15)

        # إطار الفلاتر
        filter_frame = tk.Frame(self, bg="#f9f9f9")
        filter_frame.pack(pady=10)

        self.filter_var = tk.StringVar(value="all")
        filters = [("اليوم", "today"), ("الأسبوع", "week"), ("الشهر", "month"), ("الكل", "all")]
        for (text, val) in filters:
            rb = ttk.Radiobutton(filter_frame, text=text, variable=self.filter_var, value=val, command=self.load_data)
            rb.pack(side=tk.LEFT, padx=15)

        # إطار الجدول
        table_frame = tk.Frame(self)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        columns = ("id", "product_name", "quantity", "total", "date")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
        self.tree.heading("id", text="رقم العملية")
        self.tree.heading("product_name", text="اسم المنتج")
        self.tree.heading("quantity", text="الكمية")
        self.tree.heading("total", text="المبلغ")
        self.tree.heading("date", text="التاريخ")

        self.tree.column("id", width=100, anchor=tk.CENTER)
        self.tree.column("product_name", width=250, anchor=tk.W)
        self.tree.column("quantity", width=80, anchor=tk.CENTER)
        self.tree.column("total", width=100, anchor=tk.CENTER)
        self.tree.column("date", width=120, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # شريط الحالة
        self.status_var = tk.StringVar()
        status_bar = tk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, bg="#eaeaea")
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def load_data(self):
        self.tree.delete(*self.tree.get_children())
        filter_type = self.filter_var.get()
        today = datetime.now()

        all_sales = get_sales()
        filtered_sales = []

        if filter_type == "today":
            filtered_sales = [sale for sale in all_sales if sale[4] == today.strftime("%Y-%m-%d")]
        elif filter_type == "week":
            week_ago = today - timedelta(days=7)
            filtered_sales = [sale for sale in all_sales if week_ago.strftime("%Y-%m-%d") <= sale[4] <= today.strftime("%Y-%m-%d")]
        elif filter_type == "month":
            month_ago = today - timedelta(days=30)
            filtered_sales = [sale for sale in all_sales if month_ago.strftime("%Y-%m-%d") <= sale[4] <= today.strftime("%Y-%m-%d")]
        else:
            filtered_sales = all_sales

        for sale in filtered_sales:
            sale_id, product_id, quantity, total, date = sale
            product_name = self.products_dict.get(product_id, "غير معروف")
            self.tree.insert("", tk.END, values=(sale_id, product_name, quantity, f"{total:.2f}", date))

        self.status_var.set(f"عدد العمليات المعروضة: {len(filtered_sales)}")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # إخفاء النافذة الرئيسية
    window = SalesReportWindow(root)
    window.mainloop()
