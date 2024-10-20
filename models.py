from typing import Optional
from sqlalchemy import Column, Integer, String, Date
from database import Base
from pydantic import BaseModel



class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    mobile_number = Column(String, unique=True)
    date_of_birth = Column(Date)
    hashed_password = Column(String)

class LoginModel(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    password: str