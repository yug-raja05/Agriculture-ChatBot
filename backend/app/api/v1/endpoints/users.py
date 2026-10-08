import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.api.deps import get_db, get_current_user
from app.models.user import UserDB
from app.models.profile import FarmerProfileDB
from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse

router = APIRouter()

@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_in: ProfileCreate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Creates a new farmer profile for the logged in user.
    """
    existing_profile = await db["profiles"].find_one({"user_id": current_user.id})
    if existing_profile:
        raise HTTPException(
            status_code=400,
            detail="Profile already exists for this user. Use PUT to modify it."
        )
        
    profile_id = str(uuid.uuid4())
    profile_db = FarmerProfileDB(
        _id=profile_id,
        user_id=current_user.id,
        fullname=profile_in.fullname,
        phone=profile_in.phone,
        location=profile_in.location,
        farm_size_hectares=profile_in.farm_size_hectares,
        primary_crops=profile_in.primary_crops,
        soil_profile=profile_in.soil_profile
    )
    
    await db["profiles"].insert_one(profile_db.model_dump(by_alias=True))
    return profile_db

@router.get("/profiles/me", response_model=ProfileResponse)
async def get_my_profile(
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Gets the profile of the current logged in user.
    """
    profile = await db["profiles"].find_one({"user_id": current_user.id})
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found. Please create a profile first."
        )
    return FarmerProfileDB(**profile)

@router.put("/profiles/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_in: ProfileUpdate,
    current_user: UserDB = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Modifies profile fields for the logged in user.
    """
    profile = await db["profiles"].find_one({"user_id": current_user.id})
    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found."
        )
        
    update_data = profile_in.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.now(timezone.utc)
    
    await db["profiles"].update_one(
        {"user_id": current_user.id},
        {"$set": update_data}
    )
    
    updated_profile = await db["profiles"].find_one({"user_id": current_user.id})
    return FarmerProfileDB(**updated_profile)
