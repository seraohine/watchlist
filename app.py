from flask import Flask, render_template, request, redirect, url_for , flash
from flask_sqlalchemy import SQLAlchemy
import os
import sys
import click
from markupsafe import Markup
import markdown2
import secrets
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import LoginManager , UserMixin , login_user , logout_user , login_required , current_user

WIN = sys.platform.startswith('win')
if WIN:
    prefix = 'sqlite:///'
else:
    prefix = 'sqlite:////'

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY',secrets.token_hex(16))
app.config['SQLALCHEMY_DATABASE_URI'] = prefix + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):  # 创建用户加载回调函数，接受用户 ID 作为参数
    user = User.query.get(int(user_id))  # 用 ID 作为 User 模型的主键查询对应的用户
    return user  # 返回用户对象

#数据库定义
class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    username = db.Column(db.String(20))
    password_hash = db.Column(db.String(128))   #采用哈希

    def set_password(self,password):    #设置密码
        self.password_hash = generate_password_hash(password)

    def validate_password(self,password):       #检查密码是否正确，返回bool值
        return check_password_hash(self.password_hash,password)


#用户登录逻辑
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if not username or not password:
            flash('Invalid input.')
            return redirect(url_for('login'))

        user = User.query.first()
        # 验证用户名和密码是否一致
        if username == user.username and user.validate_password(password):
            login_user(user)  # 登入用户
            flash('Login success.')
            return redirect(url_for('index'))  # 重定向到主页

        flash('Invalid username or password.')  # 如果验证失败，显示错误消息
        return redirect(url_for('login'))  # 重定向回登录页面

    return render_template('login.html')

@app.route('/logout')
@login_required  # 用于视图保护，后面会详细介绍
def logout():
    logout_user()  # 登出用户
    flash('Goodbye.')
    return redirect(url_for('index'))  # 重定向回首页

@app.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        name = request.form['name']

        if not name or len(name) > 20:
            flash('Invalid input.')
            return redirect(url_for('settings'))

        current_user.name = name
        # current_user 会返回当前登录用户的数据库记录对象
        # 等同于下面的用法
        # user = User.query.first()
        # user.name = name
        db.session.commit()
        flash('Settings updated.')
        return redirect(url_for('index'))

    return render_template('settings.html')


class Projects(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60))
    content = db.Column(db.Text)


@app.cli.command()
@click.option('--drop', is_flag=True, help='Create after drop.')
def initdb(drop):
    if drop:  # init the database
        db.drop_all()
    db.create_all()
    click.echo('Initialized database')

@app.cli.command()
@click.option('--username', prompt=True, help='The username used to login.')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='The password used to login.')
def admin(username, password):
    """Create user."""
    db.create_all()

    user = User.query.first()
    if user is not None:
        click.echo('Updating user...')
        user.username = username
        user.set_password(password)  # 设置密码
    else:
        click.echo('Creating user...')
        user = User(username=username, name='Admin')
        user.set_password(password)  # 设置密码
        db.session.add(user)

    db.session.commit()  # 提交数据库会话
    click.echo('Done.')


@app.context_processor
def inject_user():
    user = User.query.first()
    return dict(user=user)


@app.route('/',methods = ['GET','POST'])
def index():
    if request.method == 'POST':
        if not current_user.is_authenticated:
            return redirect(url_for('index'))
        title = request.form.get('title')
        if title:
            new_project = Projects(title = title , content = '')
            db.session.add(new_project)
            db.session.commit()
            flash('Add successfully.')
            
    projects = Projects.query.all()
    return render_template('index.html', projects=projects)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route('/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Projects.query.get_or_404(project_id)

    if request.method == 'POST':
        content = request.form['content']

        project.content = Markup(markdown2.markdown(content))
        db.session.commit()
        flash('updated successfully')
        return redirect(url_for('index'))

    return render_template('edit_project.html', project=project)


@app.route('/view/<int:project_id>')
def view_project(project_id):
    project = Projects.query.get_or_404(project_id)
    return render_template('view_project.html', project=project)

@app.route('/movie/delete/<int:project_id>', methods=['POST'])  # 限定只接受 POST 请求
@login_required
def delete(project_id):
    project = Projects.query.get_or_404(project_id)  # 获取电影记录
    db.session.delete(project)  # 删除对应的记录
    db.session.commit()  # 提交数据库会话
    flash('deleted.')
    return redirect(url_for('index'))  # 重定向回主页
