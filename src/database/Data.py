import psycopg2
from Task.Task import Task, Status
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class DataHandler:
    def __init__(self) -> None:
        # set up PostgreSQL connection 
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv('db_name'),
                user=os.getenv('db_user'),
                password=os.getenv('db_password'),
                host=os.getenv('db_host'),
                port=os.getenv('db_port')
            )
            self.cur = self.conn.cursor()
            print("Connected to PostgreSQL successfully!")
        except psycopg2.Error as e:
            print(f"Error connecting to PostgreSQL: {e}")

    # register new user in database, email must be unqiue 
    def create_account(self, name, email, hash, user_id):

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
    
    # get a user's hash 
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
    
    # get a user's user_id
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
    
    # set a new hash for a user
    def set_password_hash_for_user(self, user_id, hash):
        self.cur.execute("""
                         UPDATE TABLE users 
                         SET hash = %s
                         WHERE user_id = %s
                        """,
                        (hash, user_id))
        self.conn.commit()

    # add a new task for a given user
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

    # change a task's status 
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

    # change a task's title and decription 
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

    # delete a task
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

    # get a list of tasks for a user based on page and limit with an optional status filter 
    def get_tasks(self, user_id, status, page, limit):
        offset = (page - 1)*limit # page is 1-indexed but offset is 0-indexed 
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

