from flask import Flask, redirect, render_template, request, url_for, session, flash
from datetime import datetime
import mysql.connector
import os
from models import PostsMansger
# import bcrypt
# from werkzeug.security import generate_password_hash

 #시험중
 #플라스크 정의
app = Flask(__name__)

# 비밀 키 설정 (세션을 사용하려면 필요)
app.secret_key = 'your_secret_key'

app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

mana = PostsMansger()

# 간단한 사용자 예시 (실제 서비스에서는 데이터베이스 사용)
users = {'user2': 'password123', 'user3': 'mypassword'}


@app.route('/')
def index():
    posts = mana.all_posts()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:id>')
def view_post(id):
    post = mana.get_post_by_id(id)
    if post:
        return render_template('view.html', post=post)
    return "게시글을 찾을 수 없습니다.", 404

@app.route('/post/add', methods=['GET', 'POST'])
def add_post():
    if 'user_id' not in session:
        flash('로그인 후 게시글을 작성할 수 있습니다.', 'error')
        return redirect(url_for('login'))  # 로그인하지 않으면 로그인 페이지로 리다이렉트

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        
        file = request.files['file']
        filename = file.filename if file else None

        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        author = session['user_id']  # 로그인된 사용자 아이디를 author로 설정

        # 게시글 추가
        if mana.add_post(None, title, content, filename, 0, author):
            return redirect('/')
        return "게시글 추가 실패", 400
    return render_template('add.html')

@app.route('/post/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    if 'user_id' not in session:
        flash('로그인 후 게시글을 수정할 수 있습니다.', 'error')
        return redirect(url_for('login'))  # 로그인하지 않으면 로그인 페이지로 리다이렉트

    post = mana.get_post_by_id(id)
    if not post:
        return "게시글을 찾을 수 없습니다.", 404

    # 게시글 작성자가 아니면 수정할 수 없도록 제한
    if post['author'] != session['user_id']:
        flash('자신이 작성한 게시글만 수정할 수 있습니다.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        visit = request.form['visit']
        author = session['user_id']  # 로그인된 사용자 아이디를 author로 설정
        
        file = request.files['file']
        filename = file.filename if file else None

        if filename:
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        if mana.update_post(id, title, content, filename, visit, author):
            return redirect('/')
        return "게시글 수정 실패", 400
    return render_template('edit.html', post=post)

@app.route('/post/delete/<int:id>')
def delete_post(id):
    if 'user_id' not in session:
        flash('로그인 후 게시글을 삭제할 수 있습니다1212.', 'error')
        return redirect(url_for('login'))  # 로그인하지 않으면 로그인 페이지로 리다이렉트

    post = mana.get_post_by_id(id)
    if not post:
        return "게시글을 찾을 수 없습니다.", 404

    # 게시글 작성자가 아니면 삭제할 수 없도록 제한
    if post['author'] != session['user_id']:
        flash('자신이 작성한 게시글만 삭제할 수 있습니다.', 'error')
        return redirect(url_for('index'))

    if mana.delete_post(id):
        return redirect(url_for('index'))
    return "게시글 삭제 실패12", 400

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uid = request.form['userid']
        pwd = request.form['password']

        # 데이터베이스에서 사용자 정보를 가져옴
        try:
            mana.connect()
            sql = "SELECT * FROM users WHERE uid = %s"
            mana.cursor.execute(sql, (uid,))
            user = mana.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"사용자 확인 실패: {error}")
            flash('오류가 발생했습니다. 다시 시도해주세요.', 'error')
            return redirect(url_for('login'))  # 오류 발생 시 로그인 페이지로 리다이렉트
        finally:
            mana.disconnect()

        # 사용자와 비밀번호가 일치하는지 텍스트로 비교
        if user and user['pwd'] == pwd:  # 비밀번호 확인
            session['user'] = user['uname']  # 세션에 사용자 이름 저장
            flash('로그인 성공!', 'success')
            return redirect(url_for('index'))  # 로그인 성공 후 홈 페이지로 리다이렉트
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'error')
            return redirect(url_for('login'))  # 로그인 실패 시 로그인 페이지로 리다이렉트

    return render_template('login.html')  # GET 요청 시 로그인 페이지 렌더링


@app.route('/logout')
def logout():
    # 세션 초기화 (로그아웃)
    session.clear()
    flash('로그아웃 되었습니다.', 'success')
    return redirect(url_for('index'))  # 홈 페이지로 리다이렉트

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # 폼 데이터 가져오기
        uid = request.form.get('userid')
        pwd = request.form.get('password')
        email = request.form.get('email')
        uname = request.form.get('username')

        # 필수 입력값 확인
        if not uid or not pwd or not email or not uname:
            flash('모든 필드를 입력해주세요.', 'error')
            return redirect(url_for('register'))

        # 중복 사용자 확인
        try:
            mana.connect()
            sql = "SELECT * FROM users WHERE uid = %s"
            mana.cursor.execute(sql, (uid,))
            existing_user = mana.cursor.fetchone()
        except mysql.connector.Error as error:
            print(f"사용자 확인 실패: {error}")
            flash('오류가 발생했습니다. 다시 시도해주세요.', 'error')
            return redirect(url_for('register'))
        finally:
            mana.disconnect()

        # 중복 사용자 처리
        if existing_user:
            flash('이미 존재하는 아이디입니다.', 'error')
            return redirect(url_for('register'))

        # 새 사용자 추가 (비밀번호 해싱 없이 저장)
        try:
            mana.connect()
            sql = """
                INSERT INTO users (uid, uname, pwd, email, created_at) 
                VALUES (%s, %s, %s, %s, NOW())
            """
            mana.cursor.execute(sql, (uid, uname, pwd, email))
            mana.connection.commit()
            flash('회원가입 성공! 로그인해주세요.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as error:
            print(f"회원가입 실패: {error}")
            flash('회원가입에 실패했습니다. 다시 시도해주세요.', 'error')
        finally:
            mana.disconnect()

    return render_template('register.html')




if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5003, debug=True)
