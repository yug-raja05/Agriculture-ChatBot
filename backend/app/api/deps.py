from typing import Generator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.config import settings
from app.core.database import db_manager, get_db
from app.core.security import ALGORITHM
from app.models.user import UserDB, UserRole
from app.schemas.token import TokenData

# OAuth2 authentication scheme configuration
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db)
) -> UserDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        token_data_sub: str = payload.get("sub")
        token_data_roles: List[str] = payload.get("roles", [])
        if token_data_sub is None:
            raise credentials_exception
        token_data = TokenData(sub=token_data_sub, roles=token_data_roles)
    except JWTError:
        raise credentials_exception
        
    user_doc = await db["users"].find_one({"_id": token_data.sub})
    if user_doc is None:
        raise credentials_exception
        
    return UserDB(**user_doc)

def check_role(allowed_roles: List[UserRole]):
    """
    Dependency checking user authorization roles.
    """
    async def role_dependency(current_user: UserDB = Depends(get_current_user)):
        # Check if the user shares any allowed role
        if not any(role in current_user.roles for role in allowed_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account role does not have permission to access this resource"
            )
        return current_user
    return role_dependency
