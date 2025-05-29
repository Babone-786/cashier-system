from db_manager import create_tables, add_user

if __name__ == "__main__":
    # إنشاء الجداول في قاعدة البيانات (المستخدمين والمنتجات)
    create_tables()

    # إضافة مستخدمين تجريبيين
    add_user('admin', '1234', 'admin')
    add_user('cashier', '0000', 'cashier')

    print("تم إنشاء الجداول وإضافة المستخدمين التجريبيين.")
