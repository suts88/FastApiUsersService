from pydantic import BaseModel
from datetime import date

class UserDto(BaseModel):
    name: str
    email: str
    date_of_birth: date
    mobile_number: str
    password :str