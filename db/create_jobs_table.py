import sqlite3


con= sqlite3.connect("revhire.db")
# print(con.total_changes)
cur=con.cursor()
cur.execute('''CREATE TABLE if not exists job(
        job_id INTEGER PRIMARY KEY AUTOINCREMENT,
        description VARCHAR(500),
        skills_req varchar(100), 
        applied_by varchar(100),
        posted_by INTEGER ,
        FOREIGN KEY (posted_by) REFERENCES users(id)
        )''')


