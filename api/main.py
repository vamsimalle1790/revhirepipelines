from fastapi import FastAPI, HTTPException
from models.user import user_model
from models.login import login_model
from models.applications import application_model
from db import users_requests
from db import job_requests
import jwt # type: ignore


SECRET_KEY = "hello-world"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1



app = FastAPI()

li = []

@app.get("/")
def home(name : str = "hello"):
    print("get", name)
    return {"get": name}

@app.post("/signup")
def signup(ud:user_model):
    ret = users_requests.user_creation(ud)
    #signup takes the details and send to db
    return ret

@app.post("/login")
def login(ud:login_model):
    #login details for login
    # creating an session token with jwt 
    data = users_requests.user_login(ud)

    if data == False:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    return {"token": jwt.encode(data,SECRET_KEY,ALGORITHM)}

@app.get("/user/id")
def display_user_details(token:str):
    #returning user details with token
    ud = jwt.decode(token,SECRET_KEY,ALGORITHM)
    data = users_requests.user_details(ud["mail"])
    if data == False:
        raise HTTPException(status_code=401, detail="Invalid token")
    return data

@app.delete("/logout")
def logout(token : str):
    
    return {"logout":"need to be written"}

    #logging out/ removing token
@app.delete("/user/id")
def delete_profile(token : str):
    #delete the profile with jwt
    ud = jwt.decode(token,SECRET_KEY,ALGORITHM)
    data = users_requests.user_delete(ud["id"])
    if data == False:
        raise HTTPException(status_code=401, detail="User details not found")
    if data == True:
        return "deleted sucessfully"

"""
    job method for user
"""

@app.get("/jobs")
def lsit_all_jobs():
    #returning all the job list
    data = job_requests.get_all_job_posts()
    return data

@app.post("/apply")
def job_apply(ud_token:str, job_id):
    #apply for a job with userid and jobid
    ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
    if ud["role"] == 1:
        raise HTTPException(status_code=401, detail="You are an employee... register yourself as an jobseeker")
    
    job_requests.apply_jobs(ud["id"],job_id)
    raise HTTPException(status_code=200, detail="Updated sucessfully")


@app.get("/job/id")
def view_job_by_id(ud_token:str):
    ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
    if ud["role"] == 0:
        raise HTTPException(status_code=401, detail="Only employers can view their job posts")
    data = job_requests.job_fetch_by_id(ud["id"])
    #take employeeid and fetch all the jobs they posted
    return data

@app.get("/applications/user_id")
def get_applied_jobs(ud_token:str):
    
    ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
    data = job_requests.get_applied_jobs(ud["id"])
    #take userid as input and show all the jobs he applied
    return data


@app.delete("/application/id")
def applicaiton_withdraw():
    #take the application id and remove it
    return "removed sucessfully"

"""
    job methods of employee
"""
@app.post("/job/create")
def create_job(jd : application_model, ud_token: str):
    #only employee can create
    #take employee id and create job post
    ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
    if ud["role"] == 0:
        raise HTTPException(status_code=401, detail="Only employers can create job posts")

    data = job_requests.job_creation(ud["id"], jd)
    return {"application" : "done", "data" : data}

@app.get("/jobs/user_id")
def get_jobs_posted_by_employee(ud_token:str):
    ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
    if ud["role"] == 0:
        raise HTTPException(status_code=401, detail="Only employers can view their job posts")
    data = job_requests.job_posted_by_employee(ud["id"])
    #take employeeid and fetch all the jobs they posted
    return data

@app.delete("/job/id")
def delete_job_by_id(job_id, token):
    #deleting that job id along with changing application status off all the applicants
    ud = jwt.decode(token,SECRET_KEY,ALGORITHM)
    data = users_requests.job_delete(job_id, ud["id"])
    if data == False:
        raise HTTPException(status_code=401, detail="User details not found")
    if data == True:
        return "deleted sucessfully"
    

@app.get("/applications/job_id")
def get_all_the_job_applicants(job_id, ud_token):
    #fetch all the applicants details that applied for the job
    ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
    if ud["role"] == 0:
        raise HTTPException(status_code=401, detail="Only employers can view their job post applicants")
    data = job_requests.get_job_applicants(ud["id"], job_id)
    #take employeeid and fetch all the jobs they posted
    return data

if __name__ == "__main__":
    print("file running")
