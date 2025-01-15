from datetime import datetime
import mysql.connector
from flask import session

# import bcrypt
# from werkzeug.security import generate_password_hash

class PostsMansger:
    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                # MySQL 연결 정보 (예: host, user, password, db 등)
                host="10.0.66.24",
                user="tulips",
                password="2345",
                database="board_db"
            )
            self.cursor = self.connection.cursor(dictionary=True)  # 커서 초기화
        except mysql.connector.Error as error:
            print(f"데이터베이스 연결 실패: {error}")

    def disconnect(self):
        if self.cursor:
            self.cursor.close()  # 커서 닫기
        if self.connection and self.connection.is_connected():
            self.connection.close()

    def all_posts(self):
        try:
            self.connect()
            sql = "SELECT * FROM posts"
            self.cursor.execute(sql)
            return self.cursor.fetchall()
        except mysql.connector.Error as error:
            print(f"데이터 조회 실패: {error}")
            return []
        finally:
            self.disconnect()

    def add_post(self, id, title, content, filename, visit, author):
        try:
            self.connect()
            sql = """
                INSERT INTO posts (id, title, content, filename, created_at, visit, author) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (id, title, content, filename, datetime.now(), visit, author)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시판 추가 실패: {error}")
            return False
        finally:
            self.disconnect()

    def get_post_by_id(self, id):
        try:
            print(f"받은 게시글 ID: {id}")  # 전달된 ID를 출력
            self.connect()  # 데이터베이스 연결
            sql = "SELECT * FROM posts WHERE id = %s"
            self.cursor.execute(sql, (id,))
            post = self.cursor.fetchone()  # 해당 ID의 게시글을 하나 가져오기
            if post:
                print(f"게시글 조회 성공: {post}")  # 게시글 정보 출력
            else:
                print("게시글이 없습니다.")  # 게시글이 없는 경우
            return post
        except mysql.connector.Error as err:
            print(f"쿼리 실행 오류: {err}")  # 오류 메시지 출력
            return None
        finally:
            self.disconnect()  # 데이터베이스 연결 해제


    def update_post(self, id, title, content, filename, visit, author):
        try:
            self.connect()
            if filename:
                sql = """
                    UPDATE posts 
                    SET title = %s, content = %s, filename = %s, visit = %s, author = %s 
                    WHERE id = %s
                """
                values = (title, content, filename, visit, author, id)
            else:
                sql = """
                    UPDATE posts 
                    SET title = %s, content = %s, visit = %s, author = %s 
                    WHERE id = %s
                """
                values = (title, content, visit, author, id)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시판 수정 실패: {error}")
            return False
        finally:
            self.disconnect()

    def delete_post(self, id):
        try:
            self.connect()
            sql = "DELETE FROM posts WHERE id = %s"
            values = (id,)
            self.cursor.execute(sql, values)
            self.connection.commit()
            return True
        except mysql.connector.Error as error:
            print(f"게시판 삭제 실패: {error}")
            return False
        finally:
            self.disconnect()

    def add_user(self, uid, pwd, uname):
        try:
            self.connect()  # 데이터베이스 연결
            
            print("데이터베이스 연결 성공")  # 데이터베이스 연결 확인 로그
            sql = """
            INSERT INTO users (uid, pwd, uname, created_at) 
            VALUES (%s, %s, %s, NOW())
            """
            values = (uid, pwd, uname)
            self.cursor.execute(sql, values)
            self.connection.commit()  # 트랜잭션 커밋
            print("사용자 추가 완료")  # 쿼리 실행 완료 로그
            return True
        except mysql.connector.Error as error:
            print(f"사용자 추가 실패: {error}")  # 오류 메시지 출력
            return False
        finally:
            self.disconnect()  # 데이터베이스 연결 해제






