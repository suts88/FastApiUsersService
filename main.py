from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from database import get_db, SessionLocal, engine
from models import Base
from starlette import status
from starlette.responses import JSONResponse
from passlib.context import CryptContext
import datetime
import jwt
import logging


from dtos import UserDto
from models import Users, LoginModel

import os

# TOKEN
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

def create_access_token(user: Users):
    payload = {
        "id": user.id,
        "email": user.email,
        "exp": datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
    }
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


# DEPENDENCIES
db_dependency = Annotated[Session, Depends(get_db)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# API
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Erlaube allen Ursprüngen (nicht empfohlen für Produktion)
    allow_credentials=True,
    allow_methods=["*"],  # Erlaube alle Methoden (GET, POST usw.)
    allow_headers=["*"],  # Erlaube alle Header
)

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)



# Logger konfigurieren
logger = logging.getLogger(__name__)

@app.post("/api/v1/register", status_code=status.HTTP_201_CREATED)
async def register_new_user(db: db_dependency,
                            register_user: UserDto):
    # Logge die eingehenden Daten
    logger.info("Received registration request: %s", register_user)

    # Prüfen, ob die E-Mail bereits existiert
    existing_user = db.query(Users).filter(Users.email == register_user.email).first()
    if existing_user:
        logger.warning(f"Registration attempt failed: Email {register_user.email} already exists.")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )

    try:
        # Logge, dass der Benutzer erstellt wird
        logger.info(f"Creating new user: {register_user.email}")

        new_user = Users(
            name=register_user.name,
            email=register_user.email,
            mobile_number=register_user.mobile_number,
            date_of_birth=register_user.date_of_birth,
            hashed_password=bcrypt_context.hash(register_user.password),
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        # Erfolgreiche Antwort loggen
        logger.info(f"User {register_user.email} created successfully.")
        return JSONResponse(status_code=status.HTTP_201_CREATED, content={"message": "User created successfully."})

    except IntegrityError as e:
        # Logge den Fehler
        logger.error(f"IntegrityError during user creation: {e}")
        # Rollback bei Fehlern während der DB-Operation
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while creating the user."
        )

@app.post("/api/v1/login", status_code=status.HTTP_200_OK)
async def login_user(login_data: LoginModel, db: db_dependency):
    # Checks if email or phone_number is available
    if not login_data.email and not login_data.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="E-Mail or Phone number must be provided"
        )
    # Searches User in DB
    if login_data.email:
        db_user = db.query(Users).filter(Users.email == login_data.email).first()
    else:
        db_user = db.query(Users).filter(Users.phone_number == login_data.phone_number).first()

    # If User not in DB
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not find User in DB, Please try again or register"
        )
    # User in DB
    else:
        # PW Validation
        password_valid = bcrypt_context.verify(login_data.password, db_user.hashed_password)
        # PW not correct
        if not password_valid :
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        # Validation Success
        else:
            access_token = create_access_token(db_user)
            return {"access_token": access_token, "token_type": "bearer"}