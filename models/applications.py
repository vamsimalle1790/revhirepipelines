from pydantic import BaseModel

class application_model(BaseModel):

    job_id :int = None
    description :str
    skills_req : str 
    applied_by :str = None
    posted_by : int
