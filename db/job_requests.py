from fastapi import HTTPException
from models.applications import application_model
from models.user import user_model
import sqlite3
import json

database = "revhire.db"
def job_creation(id:int, jd:application_model):
    
    con= sqlite3.connect(database)
    cur=con.cursor()
    cur.execute("insert into job(description,skills_req,posted_by)values(?,?,?)",
                (jd.description,jd.skills_req,id))
    con.commit()
    con.close()
    return {"job created":"sucess"}

def job_fetch_by_id(id:int):

    con= sqlite3.connect(database)
    cur=con.cursor()
    cur.execute(f"select*from job where job_id='{id}'")

    columns = [column[0] for column in cur.description]
    data = [dict(zip(columns, row)) for row in cur.fetchall()]

    z = json.dumps(data)
    z = json.loads(z)

    print(z)
    
    con.close()
    dic = {}
    j = 0
    for i in z:
        dic[j] = i
        j +=1
    return dic

def job_posted_by_employee(id:int):
    con= sqlite3.connect(database)
    cur=con.cursor()
    cur.execute(f"select*from job where posted_by='{id}'")

    columns = [column[0] for column in cur.description]
    data = [dict(zip(columns, row)) for row in cur.fetchall()]

    z = json.dumps(data)
    z = json.loads(z)

    print(z)
    
    con.close()
    dic = {}
    j = 0
    for i in z:
        dic[j] = i
        j +=1
    return dic

def job_delete(job_id, us_id):
    try:

        con= sqlite3.connect(database)
        cur=con.cursor()
        x = cur.execute(f"select*from job where job_id='{job_id}'")
        y = x.fetchone()[0]
        if y == us_id:
            cur.execute(f"delete from job where job_id='{job_id}'")
        else:
            raise HTTPException(status_code=401, detail="you are not authorised to delete the job posting")
    except:
        raise HTTPException(status_code=404, detail="Job not found or connection with database")
    finally:
        con.commit()
        con.close()

def get_all_job_posts():
    try:
        con= sqlite3.connect(database)
        cur=con.cursor()
        columns = [column[0] for column in cur.description]
        data = [dict(zip(columns, row)) for row in cur.fetchall()]

        z = json.dumps(data)
        z = json.loads(z)

        # print(z, len(z), type(z[0]))
        dic = {}
        j = 0
        for i in z:
            dic[j] = i
            j+=1
        # print(dic)
        return dic
    finally:
        con.commit()
        con.close()        

def get_applied_jobs(user_id:int):
    try:
        con= sqlite3.connect(database)
        cur=con.cursor()
    
        x = cur.execute(f"SELECT * FROM applications where id = {user_id}")

        y = list(x.fetchone())

        if y[1] == None:
            raise HTTPException(status_code=404, detail="No details found")

        applied_jobs = str(y[1]).split(",")
        jobs_status = str(y[2]).split(",")

        z = dict(zip(applied_jobs, jobs_status))
        return z
    except :
        raise HTTPException(status_code=401, detail="an error occured")
    finally:
        con.commit()
        con.close()

def apply_jobs(user_id, job_id):
    try:
        con= sqlite3.connect(database)
        cur=con.cursor()
        x = cur.execute(f"SELECT * FROM applications where id = '{user_id}'")
        z = cur.execute(f"SELECT * FROM job where job_id = '{job_id}'")
        y = list(x.fetchone())
        z1 = (z.fetchone()[3])

        if z1 == None:
            applied_by = user_id
        else:
            applied_by = str(z1) + "," + job_id


        if y[1] == None:
            applied_jobs = job_id
            jobs_status = "applied"
        else:
            applied_jobs = str(y[1]) + "," + job_id
            jobs_status = str(y[2]) + "," + "applied"

        cur.execute("UPDATE applications SET application_id = '{applied_jobs}' and application_status = '{jobs_status}' WHERE job_id = '{user_id}'")
        return {"apply":"sucess"}
        
    except:
        raise HTTPException(status_code=401, detail="an error occured")
    finally:
        con.commit()
        con.close()
    
def get_job_applicants(user_id, job_id):
    try:
        con= sqlite3.connect(database)
        cur=con.cursor()
        x = cur.execute(f"select*from job where job_id='{job_id}'")
        
        y = str(x.fetchone()[3])
        if y is None:
            return {"applied_list": None}
        y = y.split(",")
        return {"applied_list":[i for i in y] }
    finally:
        con.commit()
        con.close()


        

    
