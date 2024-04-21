from pydantic import BaseModel 

class login_model(BaseModel):
    mail:str
    password:str