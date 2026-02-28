import psycopg2
from Task.Task import Task, Status
from datetime import datetime

class DataHandler:
    def __init__(self) -> None:
        try:
            self.conn = psycopg2.connect(
                dbname="task_tracker_db",
                user="postgres",
                password="",
                host="localhost",
                port="5432"
            )
            self.cur = self.conn.cursor()
            print("Connected to PostgreSQL successfully!")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")

    def create_account(self, name, email, hash, user_id):
        # check email is unqiue 
        # self.cur.execute("""
        #                  SELECT * FROM 
        #                  USERS 
        #                  WHERE email = %s
        #                  """, 
        #                  email)
        # rows = self.cur.fetchall()
        # if len(rows) > 1:
        #     raise Exception("A user with that email already exist") 
        # store new user in User table 
        # return token on success, error otherwise 
        try:
            self.cur.execute("""
                            INSERT INTO users (name, email, hash, user_id)
                            VALUES (%s, %s, %s, %s)
                            """,
                            (name, email, hash, user_id))
            self.conn.commit()
        except psycopg2.DatabaseError as e:
            self.conn.commit()
            raise
        return None
    
    def get_hash(self, email):
        try:
            self.cur.execute("""
                            SELECT hash FROM users 
                            WHERE email = %s
                            """,
                            (email, ))
            # self.conn.commit()
            row = self.cur.fetchone()
        except Exception as e:
            raise
        if row:
            return row[0]
    
    def get_user_id(self, email):
        try:
            self.cur.execute("""
                            SELECT user_id FROM users 
                            WHERE email = %s
                            """,
                            (email, ))
            # self.conn.commit()
            row = self.cur.fetchone()
        except Exception as e:
            raise
        if row:
            return row[0]
    
    def set_password_hash_for_user(self, user_id, hash):
        self.cur.execute("""
                         UPDATE TABLE users 
                         SET hash = %s
                         WHERE user_id = %s
                        """,
                        (hash, user_id))
        self.conn.commit()

    def add_task(self, user_id, task_id, title, description):
        # print(task['description'])
        try:
            self.cur.execute("""
                            INSERT INTO tasks (task_id, user_id, title, description, status, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, now(), now())
                            """,
                            (task_id, user_id, title, description, Status.TODO.name))
            self.conn.commit()
        except psycopg2.DatabaseError as e:
            raise

    def change_status(self, user_id, task_id, status):
        try:
            self.cur.execute("""
                             UPDATE tasks
                             SET status=%s, updated_at=now()
                             WHERE user_id=%s and task_id=%s
                             """,
                             (status, user_id, task_id))
        except psycopg2.DatabaseError as e:
            raise

        self.conn.commit()
        return self.cur.rowcount   

    def change_task(self, user_id, task_id, title, description):
        try:
            self.cur.execute("""
                             UPDATE tasks
                             SET title=%s, description=%s, updated_at=now()
                             WHERE user_id=%s and task_id=%s
                             """,
                             (title, description, user_id, task_id))
        except psycopg2.DatabaseError as e:
            raise

        self.conn.commit()
        return self.cur.rowcount   

    def delete_task(self, user_id, task_id):
        try:
            self.cur.execute("""
                             DELETE FROM tasks
                             WHERE user_id=%s and task_id=%s
                             """,
                             (user_id, task_id))
        except psycopg2.DatabaseError as e:
            raise

        self.conn.commit()
        return self.cur.rowcount  


    def get_tasks(self, user_id, status, page, limit):
        offset = (page - 1)*limit # 1-indexed id in table 
        if status:
            self.cur.execute("""
                            SELECT task_id, title, description, status, created_at, updated_at 
                             FROM tasks
                             WHERE user_id = %s AND status = %s
                             LIMIT %s
                             OFFSET %s
                            """,
                            (user_id, status, limit, offset)
                            )
        else:
            self.cur.execute("""
                            SELECT task_id, title, description, status, created_at, updated_at 
                             FROM tasks
                             WHERE user_id = %s
                             LIMIT %s
                             OFFSET %s
                            """,
                            (user_id, limit, offset)
                            )
        rows = self.cur.fetchall()
        data = [
            {
                "id": row[0], 
                "title": row[1],
                "description": row[2],
                "status": row[3],
                "created_at": row[4],
                "updated_at": row[5]
            } 
                for row in rows]
        return {"data": data, "page": page, "limit": limit, "total": len(data)}


    def close(self):
        self.cur.close()
        self.conn.close()
        print("Closed connection to PostgreSQL successfully")

