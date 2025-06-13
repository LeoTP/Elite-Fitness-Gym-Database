import sqlite3
import smtplib
from email.message import EmailMessage
from datetime import datetime
from datetime import date

DB = "gym_members.db"

def connect_db():
    conn = sqlite3.connect(DB)
    return conn

def create_db():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            bmi REAL,
            next_payment DATE NOT NULL
        )
        ''')

    conn.commit()
    conn.close()

def add_member(name, email, age, height, weight, next_payment):
    next_payment = str(next_payment)
    bmi = weight / (height ** 2)
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO members (name, email, age, height, weight, bmi, next_payment)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (name, email, age, height, weight, bmi, next_payment))
    #send_reminder(email, name, next_payment)
    conn.commit()
    conn.close()

def send_reminder(email, name, next_payment):
    msg = EmailMessage()
    msg.set_content(f"Hi {name}, your next gym payment is due today, {next_payment}. Please make sure to complete it on time.")
    msg['Subject'] = 'Gym Payment Reminder'
    msg['From'] = 'leohunter74@gmail.com'
    msg['To'] = email

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login('leohunter74@gmail.com', 'nduceovkywtihgxf')  # Enable "App Password" in Gmail settings
        smtp.send_message(msg)

def check_due_payments():
    today = datetime.today().date()
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name, email, next_payment FROM members")
    for name, email, next_payment in cursor.fetchall():
        next_payment_date = datetime.strptime(str(next_payment), "%Y-%m-%d").date()
        if next_payment_date <= today:
            send_reminder(email, name, str(next_payment))
    conn.close()
    
def clear_duplicates():
    conn = connect_db()
    cursor = conn.cursor()

    # Delete duplicates based on name and email, keeping the earliest one
    cursor.execute('''
    DELETE FROM members
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM members
        GROUP BY name, email
    )
    ''')

    conn.commit()
    conn.close()

    print("Duplicate members removed.")
    
def clear_database():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members")  # Delete all rows
    conn.commit()
    conn.close()
    print("All data deleted from the database.")
    
def get_all_members():
    conn = connect
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM members")
    rows = cursor.fetchall()
    
    conn.close()
    return rows

def update_member(member_id, column, value):
    conn = connect_db()
    c = conn.cursor()
    # Map column index to column name
    columns = ['id', 'name', 'email', 'age', 'height', 'weight', 'next_payment']
    col_name = columns[column]
    if col_name == 'id':
        # ID is primary key and can't be updated
        conn.close()
        return False

    try:
        c.execute(f"UPDATE members SET {col_name}=? WHERE id=?", (value, member_id))
        conn.commit()
    except Exception as e:
        conn.close()
        return False
    conn.close()
    return True
    
def main():
    create_db()
    #clear_database()
    add_member("Leo","leohunter74@gmail.com",26,5.11,18,"2025-06-09")
    check_due_payments()
    
    
    
if __name__ == "__main__":
    main()
