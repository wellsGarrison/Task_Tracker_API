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

        

    def addTask(self, description):
        # print(task['description'])

        self.cur.execute("""
                        INSERT INTO tasks (description, status, created_at, updated_at)
                        VALUES (%s, %s, %s, %s)
                         """,
                         (description, Status.TODO.name, datetime.now(), datetime.now()))
        self.conn.commit()

    def getTasks(self, status, page, limit):
        firstIndex = (page - 1)*limit + 1 # 1-indexed id in table 
        if status:
            self.cur.execute("""
                            SELECT * 
                             FROM tasks
                             WHERE status = %s AND id >= %s AND id < %s
                            """,
                            (status, firstIndex, firstIndex + limit)
                            )
        else:
            self.cur.execute("""
                            SELECT * 
                             FROM tasks
                             WHERE id >= %s AND id < %s
                            """,
                            ( firstIndex, firstIndex + limit)
                            )
        rows = self.cur.fetchall()
        data = [
            {
                "id": row[0], 
                "description": row[1],
                "status": row[2],
                "createdAt": row[3],
                "updatedAt": row[4]
            } 
                for row in rows]
        return {"data": data, "page": page, "limit": limit, "total": len(data)}


    def close(self):
        self.cur.close()
        self.conn.close()
        print("Closed connection to PostgreSQL successfully")

