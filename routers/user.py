from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
import re
import logging
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from ..models import User

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB setup
client = AsyncIOMotorClient("mongodb+srv://personalprojects123400:personalprojects786@cluster0.gamusij.mongodb.net/securefileshare?retryWrites=true&w=majority&appName=Cluster0")
MongoClient = client["securefileshare"]
try:
    client = AsyncIOMotorClient(MONGO_URI)
    MongoClient = client["securefileshare"]
    logger.info("Connected to MongoDB")
except Exception as e:
    logger.error("MongoDB connection failed: %s", e)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    logger.info("Hashing password")
    return pwd_context.hash(password)

router = APIRouter(prefix="/auth", tags=["authentication"])

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str

    @field_validator('password')
    def validate_password(cls, v):
        logger.info("Validating password strength")
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        return v

@router.post("/signup/", status_code=status.HTTP_201_CREATED)
async def signup_user(user_data: UserSignup):
    logger.info("Signup request received for email: %s", user_data.email)

    logger.info("Checking if email already exists")
    if await MongoClient.users.find_one({"email": user_data.email}):
        logger.warning("Email already registered: %s", user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    logger.info("Hashing user password")
    hashed_password = hash_password(user_data.password)

    logger.info("Creating user document")
    user_doc = {
        "name": user_data.name,
        "email": user_data.email,
        "hashed_password": hashed_password,
        "role": "USER",
        "created_at": datetime.utcnow(),
        "is_active": True
    }

    logger.info("Inserting user into MongoDB")
    result = await MongoClient.users.insert_one(user_doc)

    logger.info("User created successfully with id: %s", str(result.inserted_id))

    return {
        "id": str(result.inserted_id),
        "name": user_data.name,
        "email": user_data.email,
        "role": "USER"
    }
