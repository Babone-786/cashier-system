import sqlite3
import os
from datetime import datetime

# مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite")

def create_connection():
    return sqlite3.connect(DB_PATH)

def create_tables():
    with create_connection() as conn:
        cursor = conn.cursor()
        
        # جدول المستخدمين
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # جدول المنتجات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT
            )
        """)

        # جدول المبيعات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                total REAL NOT NULL,
                date TEXT NOT NULL,
                FOREIGN KEY(product_id) REFERENCES products(id)
            )
        """)

        # سجل الأنشطة
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                action TEXT NOT NULL,
                timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)

        # جدول الإعدادات
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        """)

        conn.commit()

# --- إدارة المستخدمين ---
def add_user(username, password, role):
    try:
        with create_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role)
            )
            conn.commit()
    except sqlite3.IntegrityError:
        print(f"المستخدم '{username}' موجود بالفعل.")
    except Exception as e:
        print("خطأ أثناء إضافة المستخدم:", e)

def check_user(username, password):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password)
        )
        result = cursor.fetchone()
        return result[0] if result else None

def get_all_users():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, username, role, created_at FROM users")
        return cursor.fetchall()

def delete_user(user_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=?", (user_id,))
        conn.commit()

def update_user_password(user_id, new_password):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
        conn.commit()

# --- إدارة المنتجات ---
def add_product(name, price, quantity):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, quantity) VALUES (?, ?, ?)",
            (name, price, quantity)
        )
        conn.commit()

def get_all_products():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, quantity FROM products")
        return cursor.fetchall()

def update_product(product_id, name, price, quantity):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE products 
            SET name=?, price=?, quantity=?, updated_at=CURRENT_TIMESTAMP
            WHERE id=?
        """, (name, price, quantity, product_id))
        conn.commit()

def delete_product(product_id):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()

# --- المبيعات ---
def add_sale(product_id, quantity, total, date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sales (product_id, quantity, total, date) VALUES (?, ?, ?, ?)",
            (product_id, quantity, total, date)
        )
        # تحديث كمية المنتج بعد البيع
        cursor.execute("UPDATE products SET quantity = quantity - ? WHERE id = ?", (quantity, product_id))
        conn.commit()

def get_sales(filter_date=None):
    with create_connection() as conn:
        cursor = conn.cursor()
        if filter_date:
            cursor.execute("SELECT * FROM sales WHERE date=?", (filter_date,))
        else:
            cursor.execute("SELECT * FROM sales")
        return cursor.fetchall()

def total_sales_today():
    today_str = datetime.now().strftime("%Y-%m-%d")
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(total) FROM sales WHERE date=?", (today_str,))
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0

# --- سجل الأنشطة ---
def log_activity(user_id, action):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO activity_log (user_id, action) VALUES (?, ?)",
            (user_id, action)
        )
        conn.commit()

def get_activity_log():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT activity_log.id, users.username, activity_log.action, activity_log.timestamp
            FROM activity_log
            JOIN users ON activity_log.user_id = users.id
            ORDER BY activity_log.timestamp DESC
        """)
        return cursor.fetchall()

# --- إعدادات النظام ---
def get_setting(key):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        result = cursor.fetchone()
        return result[0] if result else None

def set_setting(key, value):
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO settings (key, value) VALUES (?, ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (key, value))
        conn.commit()

# --- إحصائيات عامة ---
def count_products():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM products")
        result = cursor.fetchone()
        return result[0] if result else 0

def count_users():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        return result[0] if result else 0

def total_inventory_value():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(price * quantity) FROM products")
        result = cursor.fetchone()
        return result[0] if result[0] is not None else 0

# --- دوال إضافية مطابقة للاستدعاءات في الكود ---
def get_products_count():
    return count_products()

def get_users_count():
    return count_users()

def get_all_sales():
    with create_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, product_id, quantity, total, date FROM sales ORDER BY date DESC")
        return cursor.fetchall()


if __name__ == "__main__":
    # إنشاء الجداول عند تشغيل الملف مباشرة
    create_tables()
    print("تم إنشاء الجداول بنجاح إذا لم تكن موجودة.")

    # إضافة مستخدم افتراضي (تأكد ألا يكون موجود مسبقاً)
    add_user("admin", "admin123", "admin")
    print("تم إضافة المستخدم الافتراضي 'admin' إذا لم يكن موجوداً.")
