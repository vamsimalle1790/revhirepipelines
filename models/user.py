from pydantic import BaseModel

class user_model(BaseModel):
    name : str
    mail : str
    mobile : int
    role : int
    experience : str = "None"
    skills : str = "None"


class user_smodel(BaseModel):
    name : str
    mail : str
    password : str
    role : int
    mobile : int
    experience : str = "None"
    skills : str = "None"




