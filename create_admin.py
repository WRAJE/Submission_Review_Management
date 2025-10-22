# create_admin.py
import os  # <-- 1. 导入 os 模块
from app import app
from models import db, User

with app.app_context():
    # 2. 在执行任何数据库操作前，先确保 instance 文件夹存在
    # exist_ok=True 表示如果文件夹已存在，不会报错
    os.makedirs('instance', exist_ok=True)
    
    # 3. 创建所有数据库表（如果它们还不存在的话）
    # db.create_all() 是“幂等”的，多次运行也不会有问题
    db.create_all()

    # --- 现在可以安全地进行数据库操作了 ---
    
    # 检查是否已存在管理员
    admin = User.query.filter_by(is_admin=True).first()
    if admin:
        print("管理员用户已存在。")
    else:
        # 创建新管理员
        admin_username = input("请输入管理员用户名: ")
        admin_password = input("请输入管理员密码: ")
        
        new_admin = User(username=admin_username, is_admin=True)
        new_admin.set_password(admin_password)
        
        db.session.add(new_admin)
        db.session.commit()
        print(f"管理员 '{admin_username}' 创建成功！")
