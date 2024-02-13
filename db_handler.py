import sqlite3
import os

# Global variables
db_file = "profiles.db"

# Check if the database exists
if not os.path.exists(db_file):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE profiles
               (id INTEGER PRIMARY KEY,
                name TEXT,
                age INTEGER,
                picture_id TEXT,
                work TEXT,
                academics TEXT,
                distance INTEGER)
                ''')
    conn.commit()
    print("Database and table created successfully!")
    cur.close()
    conn.close()
else:
    print("Database already exists.")

def insert_into(name, age=None, picture_id=None, work=None, academics=None, distance=None,db_file=db_file):
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    cur.execute("INSERT INTO profiles (name, age, picture_id, work, academics, distance) VALUES (?,?,?,?,?,?)", (name,age,picture_id,work,academics,distance))
    conn.commit()
    print("Data entry done.")
    cur.close()
    conn.close()