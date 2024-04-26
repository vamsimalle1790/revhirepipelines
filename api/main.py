from fastapi import FastAPI, HTTPException, Depends
from models.user import user_model, user_smodel
from models.login import login_model
from models.applications import application_model, application_create_model
from db import users_requests
from db import job_requests
import jwt # type: ignore
import hashlib
import datetime as dt


SECRET_KEY = "hello-world"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60



app = FastAPI()



@app.get("/")
def home(name : str = "hello"):
    print("get", name)
    return {"get": name}

@app.post("/signup")
def signup(ud:user_smodel = Depends()):
    # Encoding the password
    ud.password = hashlib.md5(ud.password.encode()).hexdigest()
    ret = users_requests.user_creation(ud)
    #signup takes the details and send to db
    return ret

@app.post("/login")
def login(ud:login_model = Depends()):
    #login details for login
    # creating an session token with jwt 
    try:
        ud.password = hashlib.md5(ud.password.encode()).hexdigest()
        data = users_requests.user_login(ud)
    except Exception:
        raise HTTPException(status_code=401, detail="An error occured with modules")
    if data == False:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    data["time"] = dt.datetime.now().strftime("%d %m %Y %H %M %S")
    writetoken(jwt.encode(data,SECRET_KEY,ALGORITHM))
    return {"token": jwt.encode(data,SECRET_KEY,ALGORITHM)}

@app.get("/user/id")
def display_user_details():
    #returning user details with token
    try:
        ud_token = readtoken()
        if ud_token == "":
            raise HTTPException(status_code=401, detail="Login first")
        ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
        timecheck(ud["time"])


        data = users_requests.user_details(ud["mail"])
        if data == False:
            raise HTTPException(status_code=401, detail="Invalid token")
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="AN error occured while reading")

@app.delete("/logout")
def logout():
    cleartoken()
    return {"logout":"Sucess"}

    #logging out/ removing token
@app.delete("/user/id")
def delete_profile():
    #delete the profile with jwt
    token = readtoken()
    ud = jwt.decode(token,SECRET_KEY,ALGORITHM)
    timecheck(ud["time"])
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
    try:
        data = job_requests.get_all_job_posts()
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="An error occured in reading")

@app.post("/apply")
def job_apply(ud_token:str, job_id):
    #apply for a job with userid and jobid
    try:
        ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
        if ud["role"] == 1:
            raise HTTPException(status_code=401, detail="You are an employee... register yourself as an jobseeker")
        
        job_requests.apply_jobs(ud["id"],job_id)
        raise HTTPException(status_code=200, detail="Updated sucessfully")
    except Exception:
        raise HTTPException(status_code=401, detail="An error occured")

@app.get("/job/id")
def view_job_by_id(ud_token:str):
    try:
        ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
        if ud["role"] == 0:
            raise HTTPException(status_code=401, detail="Only employers can view their job posts")
        data = job_requests.job_fetch_by_id(ud["id"])
        #take employeeid and fetch all the jobs they posted
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="An error occured")

@app.get("/applications/user_id")
def get_applied_jobs(ud_token:str):
    try:
        ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
        data = job_requests.get_applied_jobs(ud["id"])
        #take userid as input and show all the jobs he applied
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="An error occured")

@app.delete("/application/id")
def applicaiton_withdraw():
    #take the application id and remove it
    return "removed sucessfully"

"""
    job methods of employee
"""
@app.post("/job/create")
def create_job(jd : application_create_model = Depends()):
      
    #only employee can create
    #take employee id and create job post
    try:
        ud_token = readtoken()
        if ud_token == "":
            raise HTTPException(status_code=401, detail="Login first")
        ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
        timecheck(ud["time"])
        if ud["role"] == 0:
            raise HTTPException(status_code=401, detail="Only employers can create job posts")
        data = job_requests.job_creation(ud["id"], jd)
        return {"application" : "done", "data" : data}
    except Exception:
        raise HTTPException(status_code=501, detail="An error occured")
        
        

@app.get("/jobs/user_id")
def get_jobs_posted_by_employee():
    try:
        ud_token = readtoken()
        if ud_token == "":
            raise HTTPException(status_code=401, detail="Login first")
            
        ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
        if ud["role"] == 0:
            raise HTTPException(status_code=401, detail="Only employers can view their job posts")
        data = job_requests.job_posted_by_employee(ud["id"])
        #take employeeid and fetch all the jobs they posted
        return data
    except Exception:
        raise HTTPException(status_code=401, detail="An exception occured")



@app.delete("/job/id")
def delete_job_by_id(job_id):
    try:
        ud_token = readtoken()
        if ud_token == "":
            raise HTTPException(status_code=401, detail="Login first")
            
        #deleting that job id along with changing application status off all the applicants
        ud = jwt.decode(ud_token,SECRET_KEY,ALGORITHM)
        print(ud)
        timecheck(ud["time"])
        data = users_requests.job_delete(job_id, ud["id"])
        if data == False:
            raise HTTPException(status_code=401, detail="User details not found")
        if data == True:
            return "deleted sucessfully"
    except Exception:
        raise HTTPException(status_code=401, detail="An error occured in the in reading")
        

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


def timecheck(time:str):
    ag = dt.datetime.strptime(time, "%d %m %Y %H %M %S") + dt.timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)
    if ag < dt.datetime.now():
        raise HTTPException(status_code=401, detail="Your login token has expired,login again")
    
def writetoken(strin):
    with open("token.txt","w") as f:
        f.write(strin)
        #print("writing completed")
    
def readtoken():
    with open("token.txt","r") as f:
        return(f.readline())
    

def cleartoken():
    with open("token.txt", "w") as f:
        return True