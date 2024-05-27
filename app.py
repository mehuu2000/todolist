from flask import Flask, render_template, redirect, request, session

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

import os

from datetime import datetime

app=Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"

db = SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    signup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Date, nullable=False)
    do = db.Column(db.String, nullable=False)
    memo = db.Column(db.String)
    User_link_id = db.Column(db.Integer, nullable=False)
    
    important = db.Column(db.Boolean, default=False)
    uni = db.Column(db.Boolean, default=False)
    private = db.Column(db.Boolean, default=False)
    task = db.Column(db.Boolean, default=False)
    #user = db.relationship('User', backref=db.backref('todos', lazy=True))
    
'''
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    important = db.Column(db.Boolean, default=False)
    uni = db.Column(db.Boolean, default=False)
    private = db.Column(db.Boolean, default=False)
    task = db.Column(db.Boolean, default=False)
    Todo_link_id = db.Column(db.Integer, nullable=False)
'''
    
with app.app_context():
    db.create_all()
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    
    


@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        users = User.query.all()
        return render_template('index.html', users=users)
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and password and check_password_hash(user.password, password):
            login_user(user)
            return redirect('/home')
        else:
            error = "※ error:登録されていない、もしくは名前かパスワードが違います ※"
            return render_template('login.html', error=error)
    
    else:
        return render_template('login.html')
        
        
    
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if not username or not password:
            error = "記入していない項目があります"
            return render_template('signup.html', error=error)
        
        if User.query.filter_by(username=username).first():
            error = "すでに登録されている名前です"
            return render_template('signup.html', error=error)
        
        user = User(username=username, password=generate_password_hash(password, method='pbkdf2:sha256'), signup_time = datetime.now().replace(microsecond=0))
        
        db.session.add(user)
        db.session.commit()
        
        return redirect('/login')
    
    else:
        return render_template('signup.html')
    

@app.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    todos = Todo.query.filter_by(User_link_id=current_user.id).order_by(Todo.day).all()
    flag = 0
    if request.method == 'POST':
        title = request.form.get('title')
        tag = request.form.get('tag')
        if not title and not tag:
            error="検索する対象を記入して下さい"
            return render_template('home.html', todos=todos, flag=flag, error=error)
        elif title and tag:
            error="検索対象は一つにして下さい"
            return render_template('home.html', todos=todos, flag=flag, error=error)
        
        if 'search_title' in request.form:
            if title:
                todos = Todo.query.filter_by(User_link_id=current_user.id).filter(Todo.do.contains(title)).order_by(Todo.day).all()
                flag=1
                
                if not todos:
                    todos = Todo.query.filter_by(User_link_id=current_user.id).order_by(Todo.day).all()
                    error = "見つかりませんでした"
                    flag=0
                    
                return render_template('home.html', todos=todos, flag=flag, error=error)
        
        elif 'search_tag' in request.form:
            if tag:
                flag = 1
                error = ""
                if tag == '重要':
                    todos = Todo.query.filter_by(User_link_id=current_user.id, important=True).order_by(Todo.day).all()
                elif tag == '大学':
                    todos = Todo.query.filter_by(User_link_id=current_user.id, uni=True).order_by(Todo.day).all()
                elif tag == 'プライベート':
                    todos = Todo.query.filter_by(User_link_id=current_user.id, private=True).order_by(Todo.day).all()
                elif tag == 'タスク':
                    todos = Todo.query.filter_by(User_link_id=current_user.id, task=True).order_by(Todo.day).all()
                else:
                    error = "見つかりませんでした"
                    flga = 0
                
                if not todos:
                    error = "見つかりませんでした"
                    flag=0
                    
                return render_template('home.html', todos=todos, flag=flag, error=error)
            
        else:
            error = "見つかりませんでした"
            return render_template('home.html', todos=todos, flag=flag, error=error)
                
    
    else:
        return render_template('home.html', todos=todos, flag=flag)
    
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        do = request.form.get('do')
        memo = request.form.get('memo')
        day = request.form.get('day')
        
        important = request.form.get('important') is not None
        uni = request.form.get('uni') is not None
        private = request.form.get('private') is not None
        task = request.form.get('task') is not None
        
        if not do or not day:
            error = "記入していない項目があります"
            return render_template('create.html', error=error)
        
        try:
            day = datetime.strptime(day, '%Y-%m-%d').date()  # 日付文字列をdateオブジェクトに変換
        except ValueError:
            error = "無効な日付形式です"
            return render_template('create.html', error=error)
        
        new_create = Todo(do=do, memo=memo, day=day, User_link_id=current_user.id, important=important, uni=uni, private=private, task=task)

        db.session.add(new_create)
        db.session.commit()
        
        return redirect('/home')

    else:
        return render_template('create.html')
    
@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    todo=Todo.query.get(id)
    
    if request.method == 'POST':
        do = request.form.get('do')
        memo = request.form.get('memo')
        day = request.form.get('day')
        
        important = request.form.get('important') is not None
        uni = request.form.get('uni') is not None
        private = request.form.get('private') is not None
        task = request.form.get('task') is not None
    
        if not do or not day:
                error = "記入していない項目があります"
                return render_template('create.html', todo=todo, error=error)
            
        try:
            day = datetime.strptime(day, '%Y-%m-%d').date()  # 日付文字列をdateオブジェクトに変換
        except ValueError:
            error = "無効な日付形式です"
            return render_template('create.html', todo=todo, error=error)
        
        if do:
            todo.do = do
        if memo:
            todo.memo = memo
        if day:
            todo.day = day
            
        todo.important = important
        todo.uni = uni
        todo.private = private
        todo.task = task
            
        db.session.commit()
        return redirect('/home')

    else:
        return render_template('update.html', todo=todo)
    
@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    todo = Todo.query.get(id)

    db.session.delete(todo)
    db.session.commit()
    return redirect('/home')
    

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')
    
    
    
if __name__ == '__main__':
    app.debug = True
    app.run()
    
    
