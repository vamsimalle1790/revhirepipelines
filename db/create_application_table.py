import sqlite3

con= sqlite3.connect("revhire.db")
# print(con.total_changes)
cur=con.cursor()
cur.execute('''CREATE TABLE if not exists applications(
        id INTEGER PRIMARY KEY ,
        application_id VARCHAR(500) ,
        application_status VARCHAR(500) 
        
        )''')


