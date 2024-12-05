from flask import Flask, render_template, redirect, request, session, url_for, flash

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user

from werkzeug.security import generate_password_hash, check_password_hash

import os

from datetime import datetime, timedelta

app=Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///todolist.db"
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30) #セッションの有効期限のsetteeい

db = SQLAlchemy(app)
login_manager=LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'  # ログインページのエンドポイントを指定
login_manager.login_message = "ログインしてください。" #ログイン失敗時のメッセージ内容
login_manager.login_message_category = "info" #上のメッセージのカテゴリーを設定

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    signup_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.DateTime, nullable=False)
    do = db.Column(db.String, nullable=False)
    User_link_id = db.Column(db.Integer, nullable=False)
    
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tag_name = db.Column(db.String, nullable=False)
    tag_color = db.Column(db.String, nullable=False)
    User_link_id = db.Column(db.Integer, nullable=False)
    Todo_link_id = db.Column(db.Integer, nullable=False) #Todoのタグの識別を数字で管理
    
class Memo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String, nullable=False)
    Todo_link_id = db.Column(db.Integer, nullable=False)
    
    check_memo = db.Column(db.Boolean, default=False)
    
with app.app_context():
    db.create_all()
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


#日付の編集
@app.template_filter('datetime_format_full')
def datetime_format_full(value, format='%Y-%m-%d %H:%M'):
    if value is None:
        return ""
    return value.strftime(format)
@app.template_filter('datetime_format_Y')
def datetime_format_Y(value, format='%Y'):
    if value is None:
        return ""
    return value.strftime(format)
@app.template_filter('datetime_format_m')
def datetime_format_m(value, format='%m'):
    if value is None:
        return ""
    return value.strftime(format)
@app.template_filter('datetime_format_d')
def datetime_format_d(value, format='%d'):
    if value is None:
        return ""
    return value.strftime(format)
@app.template_filter('datetime_format_H')
def datetime_format_H(value, format='%H'):
    if value is None:
        return ""
    return value.strftime(format)
@app.template_filter('datetime_format_M')
def datetime_format_M(value, format='%M'):
    if value is None:
        return ""
    return value.strftime(format)
#----------------
    
    


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
            next_page = request.args.get('next')  # ← ここで next パラメータを取得
            return redirect(next_page or url_for('home')) 
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
    todos_with_tags = []
    
    for todo in todos:
        tags = Tag.query.filter_by(User_link_id=current_user.id, Todo_link_id=todo.id).all()
        todos_with_tags.append((todo, tags))
        
    if request.method == 'POST':
        return render_template('home.html')
    
                
    
    else:
        return render_template('home.html', todos_with_tags=todos_with_tags)


@app.route('/<int:id>', methods=['GET', 'POST'])
@login_required
def veiw(id):
    todo = Todo.query.filter_by(id=id).first()
    tags = Tag.query.filter_by(User_link_id=current_user.id, Todo_link_id=id).all()
    memos = Memo.query.filter_by(Todo_link_id=id).all()
    
    if request.method == 'POST':
        form_data = request.form
        for memo in memos:
            checkbox_state = form_data.get(f'memo_check{memo.id}')
            memo.check_memo = checkbox_state is not None  # チェックされているかどうかを設定
        db.session.commit()
        return redirect(url_for('veiw', id=id))
    else:
        return render_template('veiw.html', todo=todo, tags=tags, memos=memos)
    
    
@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'POST':
        do = request.form.get('title')
        day = request.form.get('day')
        time = request.form.get('time')
        
        if not do or not day:
            error = "記入していない項目があります"
            return render_template('create.html', error=error)
        
        if Todo.query.filter_by(do = do).first():
            error = "使われているタイトル名です"
            return render_template('create.html', error=error, do=do)
        
        try:
            day = datetime.strptime(day, '%Y-%m-%d').date()  # 日付文字列をdateオブジェクトに変換
            
            if time:
                time = datetime.strptime(time, '%H:%M').time()
                # 日付と時間を組み合わせて datetime オブジェクトに変換
                days = datetime.combine(day, time).replace(second=0)
            else:
                # 時間が指定されていない場合、デフォルトで00:00:00を使用
                days = datetime.combine(day, datetime.min.time()).replace(second=0)
        except ValueError as e: #ValueError:
            error = f"無効な日付、時間形式です: {str(e)}" #"無効な日付、時間形式です"
            return render_template('create.html', error=error)
        
        new_create = Todo(do=do, day=days, User_link_id=current_user.id)
        db.session.add(new_create)
        db.session.commit()
        
        form_data = request.form
        
        memos = []
        memo_count = len([key for key in form_data if key.startswith('memo')])
        for i in range(1, memo_count + 1):
            memo_content = form_data.get(f'memo{i}')
            if memo_content:
                memo = Memo(content=memo_content, Todo_link_id=new_create.id)
                memos.append(memo)

        if memos:
            db.session.add_all(memos)
        
        #タグの処理
        tags = []
        tag_count = len([key for key in form_data if key.startswith('tag_name')])
        for i in range(1, tag_count + 1):
            tag_name = form_data.get(f'tag_name{i}')
            tag_color = form_data.get(f'tag_color{i}')
            
            if tag_name and tag_color:
                color_map = {
                    "黒": "black",
                    "赤": "red",
                    "緑": "green",
                    "黄": "yellow",
                    "青": "blue"
                }
                tag_color = color_map.get(tag_color, tag_color) #漢字を英語に変換(color_mapに記載されているように変換)
                
                user_id = current_user.id
                todo_id = Todo.query.filter_by(do = do).first()
                tag = Tag(tag_name=tag_name, tag_color=tag_color, User_link_id=user_id, Todo_link_id=todo_id.id)
                
                tags.append(tag)
            else:
                error = "タグ名か色が記入されていません"
                
                delete_todo = Todo.query.filter_by(do = do).first()
                memos = Memo.query.filter_by(Todo_link_id=delete_todo.id).all()
                
                for memo in memos:
                    db.session.delete(memo)
                db.session.delete(delete_todo)
                
                db.session.commit()
                
                return render_template('create.html', error=error, do=do)
        
        
        db.session.add_all(tags)
        
        db.session.commit()
        
        return redirect('/home')
    
        

    else:
        return render_template('create.html')
    
@app.route('/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update(id):
    todo = Todo.query.get(id)
    tags = Tag.query.filter_by(User_link_id=current_user.id, Todo_link_id=id).all()
    memos = Memo.query.filter_by(Todo_link_id=id).all()
    
    if request.method == 'POST':
        form_data = request.form
        
        do = form_data.get('title')
        day = form_data.get('day')
        time = form_data.get('day_time')
        
    
        if not do or not day:
                error = "記入していない項目があります"
                return render_template('create.html', todo=todo, error=error)
            
        try:
            day = datetime.strptime(day, '%Y-%m-%d').date()  # 日付文字列をdateオブジェクトに変換
            
            if time:
                time = datetime.strptime(time, '%H:%M').time()
                # 日付と時間を組み合わせて datetime オブジェクトに変換
                days = datetime.combine(day, time).replace(second=0)
            else:
                # 時間が指定されていない場合、デフォルトで00:00:00を使用
                days = datetime.combine(day, datetime.min.time()).replace(second=0)
        except ValueError as e: #ValueError:
            error = f"無効な日付、時間形式です: {str(e)}" #"無効な日付、時間形式です"
            return render_template('create.html', error=error)
        
        if do:
            todo.do = do
        if day:
            todo.day = days
        
        for tag in tags:
            tag_name = form_data.get(f'tag_name{tag.id}')
            tag_color = form_data.get(f'tag_color{tag.id}')
            
            
            if tag_name and tag_color:
                color_map = {
                    "黒": "black",
                    "赤": "red",
                    "緑": "green",
                    "黄": "yellow",
                    "青": "blue"
                }
                tag_color = color_map.get(tag_color, tag_color) #漢字を英語に変換(color_mapに記載されているように変換)
                
            tag.tag_name = tag_name
            tag.tag_color = tag_color
            
        #tagsの数を超えた分をdbに保存(add)
        new_tags = []
        now_tag_count=len(tags)
        tag_count = len([key for key in form_data if key.startswith('tag_name')])
        for i in range(1, tag_count-now_tag_count +1):
            new_tag_name = form_data.get(f'tag_name{i}')
            new_tag_color = form_data.get(f'tag_color{i}')
                
            if new_tag_name and new_tag_color:
                color_map = {
                    "黒": "black",
                    "赤": "red",
                    "緑": "green",
                    "黄": "yellow",
                    "青": "blue"
                }
                new_tag_color = color_map.get(new_tag_color, new_tag_color) #漢字を英語に変換(color_mapに記載されているように変換)
                
                user_id = current_user.id
                todo_id = Todo.query.filter_by(do = do).first()
                tag = Tag(tag_name=new_tag_name, tag_color=new_tag_color, User_link_id=user_id, Todo_link_id=todo_id.id)
                
                new_tags.append(tag)
            else:
                error = "タグ名か色が記入されていません"
                return redirect('/<int:id>/update')
        
        db.session.add_all(new_tags)
        
        #memosの数を超えた分をdbに保存
        new_memos = []
        now_memo_count=len(memos)
        memo_count = len([key for key in form_data if key.startswith('memo')])
        for i in range(1, now_memo_count-memo_count +1):
            new_memo = form_data.get(f'memo{i}')
            
            if new_memo:
                memo = Memo(content=new_memo, Todo_link_id=id)
                new_memos.append(memo)
                
        if new_memos:
            db.session.add_all(new_memos)
            
        db.session.commit()
        return redirect('/home')

    else:
        for tag in tags:
            tag_name = tag.tag_name
            tag_color = tag.tag_color
            
            tag_count=0
            if tag_name and tag_color:
                color_map = {
                    "black": "黒",
                    "red": "赤",
                    "green": "緑",
                    "yellow": "黄",
                    "blue": "青"
                }
                tag_color = color_map.get(tag_color, tag_color) #英語を感じに変換(color_mapに記載されているように変換)
                tag.tag_color = color_map.get(tag_color, tag_color)
                
        return render_template('update.html', todo=todo, tags=tags, memos=memos)
    
@app.route('/<int:id>/delete', methods=['GET'])
@login_required
def delete(id):
    todo = Todo.query.get(id)
    tags = Tag.query.filter_by(Todo_link_id=id).all()
    memos = Memo.query.filter_by(Todo_link_id=id).all()
    
    for tag in tags:
        db.session.delete(tag)

    for memo in memos:
        db.session.delete(memo)

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