from pydantic import BaseModel

class user_model(BaseModel):
    name : str
    mail : str
    mobile : int
    role : int
    password : str
    experience : str = "None"
    skills : str = "None"



