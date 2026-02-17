from fastapi import FastAPI, APIRouter, Header, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from pydantic.networks import EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")  # Ignore MongoDB's _id field
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str



# Contact Models
class ContactSubmission(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    message: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContactSubmissionCreate(BaseModel):
    name: str
    email: str
    message: str


def _require_admin(x_admin_key: Optional[str]) -> None:
    expected = os.environ.get("ADMIN_API_KEY")
    if not expected:
        logger.warning("ADMIN_API_KEY is not set; rejecting admin request")
        raise HTTPException(status_code=500, detail="Admin auth not configured")

    if not x_admin_key or x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

# Add your routes to the router instead of directly to app


@api_router.post("/contact", response_model=ContactSubmission, status_code=201)
async def create_contact_submission(payload: ContactSubmissionCreate):
    submission = ContactSubmission(**payload.model_dump())

    doc = submission.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()

    await db.contact_submissions.insert_one(doc)
    return submission


@api_router.get("/contact/recent", response_model=List[ContactSubmission])
async def get_recent_contact_submissions(
    limit: int = 20,
    x_admin_key: Optional[str] = Header(default=None, alias="x-admin-key"),
):
    _require_admin(x_admin_key)

    lim = max(1, min(int(limit), 100))
    docs = (
        await db.contact_submissions.find({}, {"_id": 0})
        .sort("created_at", -1)
        .to_list(lim)
    )

    # Convert ISO string timestamps back to datetime objects
    for d in docs:
        if isinstance(d.get("created_at"), str):
            d["created_at"] = datetime.fromisoformat(d["created_at"])

    return [ContactSubmission(**d) for d in docs]

@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()