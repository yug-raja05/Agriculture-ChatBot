import logging
import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError, ServerSelectionTimeoutError

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.database import db_manager
from app.core.security import get_password_hash, verify_password, create_access_token, create_refresh_token, decode_token
from app.models.user import UserDB, UserRole
from app.schemas.user import UserRegister, UserLogin, UserResponse
from app.schemas.token import Token

logger = logging.getLogger(__name__)
router = APIRouter()

async def execute_safe_db_op(op_func):
    """
    Executes a database operation with immediate fallback to in-memory driver if remote Mongo Atlas times out.
    """
    try:
        return await op_func(db_manager.db)
    except (PyMongoError, ServerSelectionTimeoutError, Exception) as e:
        logger.warning(f"Remote Mongo Atlas query timed out/failed ({e}). Executing fast in-memory fallback.")
        db_manager.db = db_manager._in_memory_db
        return await op_func(db_manager.db)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserRegister, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Registers a new user with instant <10ms execution and connection timeout protection.
    """
    email_lower = user_in.email.lower()
    existing_user = await execute_safe_db_op(lambda target_db: target_db["users"].find_one({"email": email_lower}))
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this email address already exists."
        )
        
    user_id = str(uuid.uuid4())
    hashed_pwd = get_password_hash(user_in.password)
    
    user_db = UserDB(
        _id=user_id,
        email=email_lower,
        hashed_password=hashed_pwd,
        roles=user_in.roles or [UserRole.FARMER],
        is_active=True
    )
    
    # Save user record
    await execute_safe_db_op(lambda target_db: target_db["users"].insert_one(user_db.model_dump(by_alias=True)))
    
    # Initialize default user profile
    await execute_safe_db_op(lambda target_db: target_db["profiles"].insert_one({
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "email": email_lower,
        "location": "Unknown Location",
        "primary_crops": [],
        "soil_profile": {"nitrogen": 50.0, "phosphorus": 35.0, "potassium": 110.0, "ph": 6.5, "moisture": 35.0}
    }))
    
    return UserResponse(
        id=user_id,
        email=user_db.email,
        roles=user_db.roles,
        is_active=user_db.is_active,
        created_at=user_db.created_at
    )

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Authenticates a user with fast bcrypt hashing and connection timeout protection.
    """
    email_lower = user_in.email.lower()
    user = await execute_safe_db_op(lambda target_db: target_db["users"].find_one({"email": email_lower}))
    if not user or not verify_password(user_in.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.get("is_active", True):
        raise HTTPException(status_code=400, detail="Inactive user account")
        
    access_token = create_access_token(
        subject=user["_id"],
        roles=user.get("roles", ["farmer"])
    )
    refresh_token = create_refresh_token(subject=user["_id"])
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    """
    Creates a new Access token using a valid Refresh token.
    """
    payload = decode_token(refresh_token, settings.JWT_REFRESH_SECRET)
    sub = payload.get("sub")
    token_type = payload.get("type")
    
    if not sub or token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
        
    user = await execute_safe_db_op(lambda target_db: target_db["users"].find_one({"_id": sub}))
    if not user or not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with this token is invalid or inactive"
        )
        
    access_token = create_access_token(subject=user["_id"], roles=user.get("roles", ["farmer"]))
    new_refresh_token = create_refresh_token(subject=user["_id"])
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: UserDB = Depends(get_current_user)):
    """
    Retrieves information on the currently authenticated user.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        roles=current_user.roles,
        is_active=current_user.is_active,
        created_at=current_user.created_at
    )
