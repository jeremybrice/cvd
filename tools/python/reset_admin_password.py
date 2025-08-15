#!/usr/bin/env python3
"""Reset admin password"""

import sqlite3
from werkzeug.security import generate_password_hash

# Connect to database
db = sqlite3.connect('cvd.db')
cursor = db.cursor()

# Reset admin password to 'UU8fz433'
password_hash = generate_password_hash('UU8fz433')
cursor.execute('''
    UPDATE users 
    SET password_hash = ?
    WHERE username = 'admin'
''', (password_hash,))

db.commit()
print("Admin password reset to 'UU8fz433'")

# Verify the update
cursor.execute("SELECT username, email, role FROM users WHERE username='admin'")
user = cursor.fetchone()
if user:
    print(f"User confirmed: {user[0]} ({user[1]}) - Role: {user[2]}")
else:
    print("Admin user not found!")

db.close()