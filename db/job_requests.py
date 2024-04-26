from fastapi import HTTPException
from models.applications import application_model, application_create_model
from models.user import user_model
import sqlite3
import json
import logging

database = "revhire.db"
def job_creation(id:int, jd:application_create_model):
    try:
        con= sqlite3.connect(database)
        cur=con.cursor()
        cur.execute("insert into job(description,skills_req,posted_by)values(?,?,?)",
                    (jd.description,jd.skills_req,id))
        con.commit()
        return {"job created":"sucess"}
    except Exception:
        con.rollback()
        raise HTTPException(status_code=401, detail="There is an problem ")
    finally:
        con.close()
        

def job_fetch_by_id(id: int):
    try:
        con = sqlite3.connect(database)
        cur = con.cursor()
        cur.execute(f"SELECT * FROM job WHERE job_id = ?", (id,))
        
        columns = [column[0] for column in cur.description]
        data = [dict(zip(columns, row)) for row in cur.fetchall()]

        con.close()

        if len(data) > 0:
            return data[0]  # Return the first job data if found
        else:
            return {"detail": "Job not found"}
    except Exception as e:
        logging.error(f"An error occurred while fetching job details: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching job details.")

def job_posted_by_employee(id:int):
    try:
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
    except Exception:
        raise HTTPException(status_code=401, detail="An error occured with db")

def job_delete(job_id, user_id):
    try:
        con = sqlite3.connect(database)
        cur = con.cursor()
        
        # Check if the job exists and if the user is authorized to delete it
        cur.execute("SELECT posted_by FROM job WHERE job_id = ?", (job_id,))
        row = cur.fetchone()
        if row:
            posted_by = row[0]
            if posted_by == user_id:
                # Delete the job if the user is authorized
                cur.execute("DELETE FROM job WHERE job_id = ?", (job_id,))
                con.commit()
                return True
            else:
                # User is not authorized to delete the job
                raise HTTPException(status_code=401, detail="You are not authorized to delete the job posting.")
        else:
            # Job not found
            raise HTTPException(status_code=404, detail="Job not found.")
    except HTTPException:
        raise
    except Exception as e:
        # Other errors
        logging.error(f"An error occurred while deleting the job: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while deleting the job.")
    finally:
        con.close()

def get_all_job_posts():
    try:
        con= sqlite3.connect(database)
        cur=con.cursor()
        cur.execute("SELECT * From job")
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
    except Exception:
        raise HTTPException(status_code=404, detail="Job not found or connection with database")
    finally:
        con.commit()
        con.close()        

def get_applied_jobs(user_id:int):
    try:
        con= sqlite3.connect(database)
        cur=con.cursor()
    
        x = cur.execute(f"SELECT * FROM applications where id = {user_id}")

        y = list(x.fetchone())

        if y[1] == "None" or y[1] == None:
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
        con = sqlite3.connect("revhire.db")
        cur = con.cursor()

        # Check if the user has already applied for this job
        cur.execute(f"SELECT * FROM applications WHERE id = ?", (user_id,))
        user_data = cur.fetchone()
        applied_jobs_str = user_data[1] if user_data else None

        # If user has applied for other jobs, append the new job ID
        if applied_jobs_str:
            applied_jobs = applied_jobs_str.split(",") + [str(job_id)]
        else:
            applied_jobs = [str(job_id)]

        # Convert list back to string
        applied_jobs_str = ",".join(applied_jobs)

        # Update the applications table
        if user_data:
            cur.execute(f"UPDATE applications SET application_id = ? WHERE id = ?", (applied_jobs_str, user_id))
        else:
            cur.execute(f"INSERT INTO applications (id, application_id, application_status) VALUES (?, ?, ?)", (user_id, applied_jobs_str, "applied"))

        # Update the job table
        cur.execute(f"SELECT applied_by FROM job WHERE job_id = ?", (job_id,))
        applied_by_data = cur.fetchone()
        applied_by_str = applied_by_data[0] if applied_by_data else None

        # Update applied_by
        if applied_by_str:
            applied_by = applied_by_str.split(",") + [str(user_id)]
        else:
            applied_by = [str(user_id)]

        # Convert list back to string
        applied_by_str = ",".join(applied_by)

        # Update the job table with the new applied_by data
        cur.execute("UPDATE job SET applied_by = ? WHERE job_id = ?", (applied_by_str, job_id))

        con.commit()
        
        return {"apply": "success"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")
    finally:
        con.close()

    
def get_job_applicants(user_id, job_id):
    try:
        con = sqlite3.connect(database)
        cur = con.cursor()
        cur.execute(f"SELECT applied_by FROM job WHERE job_id=?", (job_id,))
        row = cur.fetchone()
        
        if row is None:
            return {"applied_list": None}
        
        applied_by = row[0]
        if applied_by is None:
            return {"applied_list": None}
        
        applied_list = applied_by.split(",")
        return {"applied_list": applied_list}
    except Exception as e:
        logging.error(f"An error occurred while retrieving job applicants: {e}")
        raise
    finally:
        con.close()


def withdraw_application(application_id: int):
    try:
        con = sqlite3.connect(database)
        cur = con.cursor()

        # Update the status of the application to "withdrawn" in the applications table
        cur.execute("UPDATE applications SET application_status = 'withdrawn' WHERE id = ?", (application_id,))
        con.commit()

        # Remove the user ID from the applied_by column in the job table
        cur.execute("SELECT application_id FROM applications WHERE id = ?", (application_id,))
        applied_jobs_data = cur.fetchone()
        applied_jobs_str = applied_jobs_data[0] if applied_jobs_data else None

        if applied_jobs_str:
            applied_jobs_list = applied_jobs_str.split(",")
            for job_id in applied_jobs_list:
                cur.execute("SELECT applied_by FROM job WHERE job_id = ?", (job_id,))
                applied_by_data = cur.fetchone()
                applied_by_str = applied_by_data[0] if applied_by_data else None

                if applied_by_str:
                    applied_by_list = applied_by_str.split(",")
                    if str(application_id) in applied_by_list:
                        applied_by_list.remove(str(application_id))  # Remove the user ID
                        applied_by_str = ",".join(applied_by_list)
                        cur.execute("UPDATE job SET applied_by = ? WHERE job_id = ?", (applied_by_str, job_id))
                        con.commit()

        con.close()
        
        return {"message": "Application withdrawn successfully."}
    except Exception as e:
        logging.error(f"An error occurred while withdrawing the application: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while withdrawing the application.")

    
