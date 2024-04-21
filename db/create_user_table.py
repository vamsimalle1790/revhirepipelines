import sqlite3

con= sqlite3.connect("revhire.db")
cur=con.cursor()
cur.execute('''CREATE TABLE if not exists user(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        mail VARCHAR(100) NOT NULL UNIQUE,
        mobile INTEGER NOT NULL UNIQUE,
        role INTEGER NOT NULL,
        password VARCHAR(100) NOT NULL,
        experience VARCHAR(100) DEFAULT 0,
        skills VARCHAR(500) NULL
        )''')

con.commit()
con.close()