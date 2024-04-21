from models.user import user_model
from models.login import login_model
import sqlite3
import json

database = "revhire.db"

def user_creation(user: user_model):
    
    con= sqlite3.connect(database)
    cur=con.cursor()
    cur.execute("insert into user(name,mail,mobile,role,password,experience)values(?,?,?,?,?,?)",
          (user.name,user.mail,user.mobile,user.role,user.password,user.experience))
    con.commit()
    x = cur.execute("SELECT id from user WHERE mail = '{user.mail}'")
    y = x.fetchone()
    # print(x.fetchone()[0])
    cur.execute("insert into applications (id,application_id,application_status)values(?,?,?)",
         (y,None,None))
    con.commit()
    con.close()
    return {"deposit":"sucess"}

def user_login(ud: login_model):
    con= sqlite3.connect(database)
    cur=con.cursor()
    x=cur.execute("select mail,password from user")
    y=x.fetchall()

    if ud.mail in [i[0] for i in y] and ud.password in [i[1] for i in y]:

        cur.execute(f"select * from user where mail='{ud.mail}' AND password='{ud.password}'")
        columns = [column[0] for column in cur.description]
        data = [dict(zip(columns, row)) for row in cur.fetchall()]

        z = json.dumps(data)
        z = json.loads(z)

        con.close()
        return z[0]
    con.close()
    return False

def user_details(mail : str):
    con= sqlite3.connect(database)
    cur=con.cursor()
    x=cur.execute("select mail from user")
    y=x.fetchall()
    if mail in [i[0] for i in y]:
        cur.execute(f"select * from user where mail='{mail}'")
        columns = [column[0] for column in cur.description]
        data = [dict(zip(columns, row)) for row in cur.fetchall()]

        z = json.dumps(data)
        z = json.loads(z)

        con.close()
        return z[0]
    con.close()
    return False

def user_delete(id:str):
    con= sqlite3.connect(database)
    cur=con.cursor()
    x=cur.execute("select id from user")
    y=x.fetchall()
    try:
        if id in [i[0] for i in y]:
            cur.execute(f"delete from user where id='{id}'")
            cur.execute(f"delete from applications where id='{id}'")
            return True
        else:
            return False
    except Exception as e:
        print("error",e)
    
    finally:
        con.commit()
        con.close()




