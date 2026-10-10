import sqlite3

conn = sqlite3.connect('db.sqlite3')
cur = conn.cursor()

print("--- ADMINS ---")
try:
    admins = cur.execute("SELECT adminid, password FROM admins_adminloginmodel").fetchall()
    for admin in admins:
        print(f"ID: {admin[0]}, Pass: {admin[1]}")
    if not admins:
        print("No admins found.")
except sqlite3.OperationalError:
    print("Table admins_adminloginmodel does not exist.")

print("\n--- USERS ---")
try:
    users = cur.execute("SELECT loginid, password, status, name FROM UserRegistrations").fetchall()
    for user in users:
        print(f"Login ID: {user[0]}, Pass: {user[1]}, Status: {user[2]}, Name: {user[3]}")
    if not users:
        print("No users found.")
except sqlite3.OperationalError:
    print("Table UserRegistrations does not exist.")

conn.close()
