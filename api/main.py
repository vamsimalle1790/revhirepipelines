from fastapi import FastAPI, HTTPException, Depends
from models.user import user_smodel
from models.login import login_model
from models.applications import application_model, application_create_model
from db import users_requests, job_requests
import jwt
import hashlib
import datetime as dt
import logging

SECRET_KEY = "hello-world"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG)

# Function to handle token-related exceptions
def handle_token_exceptions():
    try:
        token = read_token()
        if not token or token == "":
            raise HTTPException(status_code=401, detail="No token found. Please log in first.")
        return token
    except Exception as e:
        logging.error(f"Error occurred while handling token exceptions: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while reading token.")

# Function to handle exceptions related to token expiration
def check_token_expiration(time):
    expiration_time = dt.datetime.strptime(time, "%d %m %Y %H %M %S") + dt.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    if expiration_time < dt.datetime.now():
        raise HTTPException(status_code=401, detail="Token has expired. Please log in again.")

# Function to read token from file
def read_token():
    try:
        with open("token.txt", "r") as f:
            return f.readline()
    except FileNotFoundError:
        logging.error("Token file not found.")
        raise HTTPException(status_code=500, detail="Token file not found.")
    except Exception as e:
        logging.error(f"Error occurred while reading token: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while reading token.")

# Function to write token to file
def write_token(token):
    try:
        with open("token.txt", "w") as f:
            f.write(token)
    except Exception as e:
        logging.error(f"Error occurred while writing token: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while writing token.")

# Function to clear token
def clear_token():
    try:
        with open("token.txt", "w") as f:
            pass
    except Exception as e:
        logging.error(f"Error occurred while clearing token: {e}")
        raise HTTPException(status_code=500, detail="Error occurred while clearing token.")

@app.post("/signup", tags=['User'])
def signup(ud: user_smodel = Depends()):
    ud.password = hashlib.md5(ud.password.encode()).hexdigest()
    try:
        ret = users_requests.user_creation(ud)
        return ret
    except Exception as e:
        logging.error(f"Error occurred during signup: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during signup.")

@app.post("/login", tags=['User'])
def login(ud: login_model = Depends()):
    try:
        ud.password = hashlib.md5(ud.password.encode()).hexdigest()
        data = users_requests.user_login(ud)
        if not data:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        data["time"] = dt.datetime.now().strftime("%d %m %Y %H %M %S")
        token = jwt.encode(data, SECRET_KEY, ALGORITHM)
        write_token(token)
        return {"token": token}
    except Exception as e:
        logging.error(f"An error occurred during login: {e}")
        raise HTTPException(status_code=401, detail="An error occurred during login.")

@app.get("/user/id", tags=['User'])
def display_user_details(token: str = Depends(handle_token_exceptions)):
    try:
        ud = jwt.decode(token, SECRET_KEY, ALGORITHM)
        check_token_expiration(ud["time"])
        data = users_requests.user_details(ud["mail"])
        if not data:
            raise HTTPException(status_code=401, detail="Invalid token")
        return data
    except Exception as e:
        logging.error(f"An error occurred while retrieving user details: {e}")
        raise HTTPException(status_code=401, detail="An error occurred while retrieving user details.")

@app.delete("/logout", tags=['User'])
def logout():
    try:
        clear_token()
        return {"logout": "Success"}
    except Exception as e:
        logging.error(f"An error occurred during logout: {e}")
        raise HTTPException(status_code=500, detail="An error occurred during logout.")

@app.delete("/user/id", tags=['User'])
def delete_profile(token: str = Depends(handle_token_exceptions)):
    try:
        ud = jwt.decode(token, SECRET_KEY, ALGORITHM)
        check_token_expiration(ud["time"])
        data = users_requests.user_delete(ud["id"])
        if not data:
            raise HTTPException(status_code=404, detail="User details not found")
        if data:
            return "Deleted successfully"
    except Exception as e:
        logging.error(f"An error occurred while deleting user profile: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while deleting user profile.")

@app.get("/jobs", tags=['Job Seeker'])
def list_all_jobs():
    try:
        data = job_requests.get_all_job_posts()
        return data
    except Exception as e:
        logging.error(f"An error occurred while fetching job posts: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching job posts.")

@app.post("/apply", tags=['Job Seeker'])
def job_apply(job_id: int, token: str = Depends(handle_token_exceptions)):
    try:
        ud = jwt.decode(token, SECRET_KEY, ALGORITHM)
        check_token_expiration(ud["time"])
        if ud["role"] == 1:
            raise HTTPException(status_code=401, detail="Only job seekers can apply for jobs.")
        job_requests.apply_jobs(ud["id"], job_id)
        return {"message": "Application successful."}
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"An error occurred while processing the job application: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the job application.")

@app.get("/job/id", tags=['Job Seeker'])
def view_job_by_id(job_id: int, token: str = Depends(handle_token_exceptions)):
    try:
        data = job_requests.job_fetch_by_id(job_id)
        return data
    except Exception as e:
        logging.error(f"An error occurred while fetching job details: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching job details.")

@app.get("/applications/user_id", tags=['Job Seeker'])
def get_applied_jobs(token: str = Depends(handle_token_exceptions)):
    try:
        ud = jwt.decode(token, SECRET_KEY, ALGORITHM)
        check_token_expiration(ud["time"])
        data = job_requests.get_applied_jobs(ud["id"])
        return data
    except Exception as e:
        logging.error(f"An error occurred while fetching applied jobs: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching applied jobs.")

@app.delete("/application/{application_id}" , tags=['Job Seeker'])
def application_withdraw(application_id: int):
    try:
        result = job_requests.withdraw_application(application_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"An error occurred while withdrawing the application: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while withdrawing the application.")

@app.post("/job/create", tags=['Employer'])
def create_job(jd: application_create_model = Depends(), token: str = Depends(handle_token_exceptions)):
    try:
        ud = jwt.decode(token, SECRET_KEY, ALGORITHM)
        check_token_expiration(ud["time"])
        if ud["role"] == 0:
            raise HTTPException(status_code=401, detail="Only employers can create job posts.")
        data = job_requests.job_creation(ud["id"], jd)
        return {"message": "Job created successfully.", "data": data}
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"An error occurred while creating the job: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while creating the job.")

@app.get("/jobs/user_id", tags=['Employer'])
def get_jobs_posted_by_employee(token: str = Depends(handle_token_exceptions)):
    try:
        ud = jwt.decode(token, SECRET_KEY, ALGORITHM)
        check_token_expiration(ud["time"])
        if ud["role"] == 0:
            raise HTTPException(status_code=401, detail="Only employers can view their job posts.")
        data = job_requests.job_posted_by_employee(ud["id"])
        return data
    except Exception as e:
        logging.error(f"An error occurred while fetching job posts: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching job posts.")

@app.delete("/job/{job_id}", tags=['Employer'])
def delete_job_by_id(job_id: int, token: str = Depends(handle_token_exceptions)):
    try:
        ud = jwt.decode(token, SECRET_KEY, ALGORITHM)
        check_token_expiration(ud["time"])
        if ud["role"] == 0:
            raise HTTPException(status_code=401, detail="Only employers can delete job postings.")
        data = job_requests.job_delete(job_id, ud["id"])
        if not data:
            raise HTTPException(status_code=404, detail="Job details not found.")
        return {"message": "Job deleted successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        logging.error(f"An error occurred while deleting the job: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while deleting the job.")

@app.get("/applications/job_id", tags=['Employer'])
def get_all_the_job_applicants(job_id: int, token: str = Depends(handle_token_exceptions)):
    try:
        ud = jwt.decode(token, SECRET_KEY, ALGORITHM)
        check_token_expiration(ud["time"])
        if ud["role"] == 0:  # Check if the user is not an employer
            raise HTTPException(status_code=401, detail="Only employers can view job applicants.")
        data = job_requests.get_job_applicants(ud["id"], job_id)
        return data
    except Exception as e:
        logging.error(f"An error occurred while fetching job applicants: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while fetching job applicants.")

