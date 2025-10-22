# app.py
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Post
from forms import LoginForm, RegisterForm, PostForm
from datetime import datetime
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = 'drh090223' # 更改这个密钥！
#app.config['SECURITY_PASSWORD_HASH'] = 'pbkdf2:sha256'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/site.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # 设置登录页面

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- 路由 ---

@app.route("/")
def index():
    # 只显示已批准的稿件
    posts = Post.query.filter_by(status='approved').order_by(Post.date_posted.desc()).all()
    return render_template('index.html', posts=posts)

@app.route("/register", methods=['GET', 'POST'])

#def register():
#    if current_user.is_authenticated:
#        return redirect(url_for('index'))
#    form = RegisterForm()
#    if form.validate_on_submit():
#        user = User(username=form.username.data, email=form.email.data)
#        user.set_password(form.password.data)
#        db.session.add(user)
#        db.session.commit()
#        flash('恭喜，注册成功！请登录。', 'success')
#        return redirect(url_for('login'))
#    return render_template('register.html', form=form)

def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 检查用户名是否已存在
        if User.query.filter_by(username=form.username.data).first():
            flash('用户名已存在，请换一个。', 'danger')
            return redirect(url_for('register'))
        
        # 创建新用户 (不再需要邮箱)
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        flash('注册成功！请登录。', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('登录失败，请检查用户名和密码。', 'error')
    return render_template('login.html', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/submit", methods=['GET', 'POST'])
@login_required
def submit():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('你的稿件已提交，等待管理员审核。', 'success')
        return redirect(url_for('index'))
    return render_template('submit.html', form=form)

# --- 管理员路由 ---

@app.route("/admin")
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(403) # 权限不足
    posts = Post.query.filter_by(status='pending').order_by(Post.date_posted.desc()).all()
    return render_template('admin.html', posts=posts)

@app.route("/admin/approve/<int:post_id>")
@login_required
def approve_post(post_id):
    if not current_user.is_admin:
        abort(403)
    post = Post.query.get_or_404(post_id)
    post.status = 'approved'
    db.session.commit()
    flash(f'稿件 "{post.title}" 已批准。', 'success')
    return redirect(url_for('admin_panel'))

@app.route("/admin/reject/<int:post_id>")
@login_required
def reject_post(post_id):
    if not current_user.is_admin:
        abort(403)
    post = Post.query.get_or_404(post_id)
    post.status = 'rejected'
    db.session.commit()
    flash(f'稿件 "{post.title}" 已拒绝。', 'success')
    return redirect(url_for('admin_panel'))

if __name__ == '__main__':
    with app.app_context():
        if not os.path.exists('instance'):
            os.makedirs('instance')
        db.create_all() # 在应用上下文中创建所有表
    app.run(debug=True)