from fastapi import FastAPI, APIRouter, Header, HTTPException, BackgroundTasks
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from pydantic.networks import EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import asyncio
import resend
from jose import jwt, JWTError
from passlib.context import CryptContext



ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix


def _env(name: str, default: Optional[str] = None) -> Optional[str]:
    val = os.environ.get(name)
    if val is None:
        return default
    return val


async def _send_contact_email(submission: "ContactSubmission") -> None:
    api_key = _env("RESEND_API_KEY")
    sender = _env("SENDER_EMAIL")
    receiver = _env("CONTACT_RECEIVER_EMAIL")

    # Graceful no-op when not configured yet (MVP-safe)
    if not api_key or api_key == "YOUR_KEY_HERE" or not sender or not receiver:
        logger.info("Resend not configured; skipping contact email delivery")
        return

    resend.api_key = api_key

    subject = f"New portfolio message from {submission.name}"
    html = (
        "<div style='font-family:Arial, sans-serif; line-height:1.5'>"
        "<h2 style='margin:0 0 8px'>New contact submission</h2>"
        f"<p style='margin:0 0 12px'><strong>Name:</strong> {submission.name}<br/>"
        f"<strong>Email:</strong> {submission.email}<br/>"
        f"<strong>Time:</strong> {submission.created_at.isoformat()}</p>"
        "<div style='padding:12px; border:1px solid #e5e7eb; border-radius:8px; background:#fafafa'>"
        f"<pre style='white-space:pre-wrap; margin:0'>{submission.message}</pre>"
        "</div>"
        "</div>"
    )

    params = {
        "from": sender,
        "to": [receiver],
        "subject": subject,
        "html": html,
        "reply_to": [str(submission.email)],
    }

    try:
        await asyncio.to_thread(resend.Emails.send, params)
        logger.info("Resend email queued for contact submission %s", submission.id)
    except Exception as e:
        logger.exception("Failed sending Resend email for submission %s: %s", submission.id, str(e))

api_router = APIRouter(prefix="/api")


# --- Auth + Logging helpers ---
PWD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _jwt_secret() -> str:
    secret = _env("JWT_SECRET")
    if not secret:
        raise RuntimeError("JWT_SECRET is not configured")
    return secret


def _jwt_expires_seconds() -> int:
    raw = _env("JWT_EXPIRES_SECONDS", "86400")
    try:
        return int(raw or 86400)
    except Exception:
        return 86400


def _hash_password(password: str) -> str:
    return PWD_CONTEXT.hash(password)


def _verify_password(password: str, password_hash: str) -> bool:
    return PWD_CONTEXT.verify(password, password_hash)


def _create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    exp = now + timedelta(seconds=_jwt_expires_seconds())
    payload = {"sub": subject, "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(payload, _jwt_secret(), algorithm="HS256")


def _require_jwt(authorization: Optional[str]) -> str:


# Auth Models
class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


async def _ensure_seed_admin() -> None:
    admin_email = _env("ADMIN_EMAIL")
    admin_password = _env("ADMIN_PASSWORD")
    if not admin_email or not admin_password:
        logger.warning("ADMIN_EMAIL/ADMIN_PASSWORD not set; admin login will fail")
        return

    existing = await db.admin_users.find_one({"email": admin_email}, {"_id": 0})
    if existing:
        return

    doc = {
        "id": str(uuid.uuid4()),
        "email": admin_email,
        "password_hash": _hash_password(admin_password),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.admin_users.insert_one(doc)
    logger.info("Seeded initial admin user: %s", admin_email)


@app.on_event("startup")
async def _startup() -> None:
    await _ensure_seed_admin()

    expires_in: int

    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    parts = authorization.split(" ")
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid Authorization header")

    token = parts[1]
    try:
        payload = jwt.decode(token, _jwt_secret(), algorithms=["HS256"])
        sub = payload.get("sub")
        if not sub:
            raise HTTPException(status_code=401, detail="Invalid token")
        return str(sub)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")




@api_router.post("/auth/login", response_model=AdminLoginResponse)
async def admin_login(payload: AdminLoginRequest):
    admin = await db.admin_users.find_one({"email": str(payload.email)}, {"_id": 0})
    if not admin:
        await _log_event("admin_login_failed", {"email": str(payload.email), "reason": "not_found"})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not _verify_password(payload.password, admin.get("password_hash", "")):
        await _log_event("admin_login_failed", {"email": str(payload.email), "reason": "bad_password"})
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = _create_access_token(subject=str(payload.email))
    await _log_event("admin_login_success", {"email": str(payload.email)})
    return AdminLoginResponse(access_token=token, expires_in=_jwt_expires_seconds())

async def _log_event(event_type: str, payload: Dict[str, Any]) -> None:
    doc = {
        "id": str(uuid.uuid4()),
        "event_type": event_type,
        "payload": payload,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    try:
        await db.app_logs.insert_one(doc)
    except Exception:
        logger.exception("Failed writing app log")



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



class ContactSubmissionPage(BaseModel):
    items: List[ContactSubmission]
    next_cursor: Optional[str] = None


class ContactSubmissionCreate(BaseModel):
    name: str
    email: EmailStr
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
async def create_contact_submission(payload: ContactSubmissionCreate, background_tasks: BackgroundTasks):
    submission = ContactSubmission(**payload.model_dump())

    doc = submission.model_dump()
    doc["created_at"] = doc["created_at"].isoformat()

    await db.contact_submissions.insert_one(doc)

    # Non-blocking email delivery (no-op if Resend not configured)
    background_tasks.add_task(_send_contact_email, submission)

    return submission


@api_router.get("/contact/recent", response_model=ContactSubmissionPage)
async def get_recent_contact_submissions(
    limit: int = 20,
    cursor: Optional[str] = None,
    x_admin_key: Optional[str] = Header(default=None, alias="x-admin-key"),
):
    _require_admin(x_admin_key)

    lim = max(1, min(int(limit), 100))

    query = {}
    if cursor:
        # created_at stored as ISO string; lexicographic compare works for ISO-8601 UTC
        query = {"created_at": {"$lt": cursor}}

    docs = (
        await db.contact_submissions.find(query, {"_id": 0})
        .sort("created_at", -1)
        .to_list(lim)
    )

    items: List[ContactSubmission] = []
    for d in docs:
        if isinstance(d.get("created_at"), str):
            d["created_at"] = datetime.fromisoformat(d["created_at"])
        items.append(ContactSubmission(**d))

    next_cursor = None
    if len(items) == lim:
        next_cursor = items[-1].created_at.isoformat()

    return ContactSubmissionPage(items=items, next_cursor=next_cursor)

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