import sqlite3

conn = sqlite3.connect("products.db")  # ينشئ الملف لو مش موجود
cursor = conn.cursor()

# إنشاء جدول المنتجات إذا مش موجود
cursor.execute("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL
)
""")

# أدخل بيانات تجريبية
cursor.execute("DELETE FROM products")  # لمسح أي بيانات سابقة (اختياري)

products = [
    ('منتج 1', 50.0, 100),
    ('منتج 2', 75.5, 50),
    ('منتج 3', 20.0, 200),
    ('منتج 4', 100.0, 30),
]

cursor.executemany("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)", products)

conn.commit()
conn.close()

print("قاعدة البيانات والجدول تم إنشاؤهم مع البيانات التجريبية.")
