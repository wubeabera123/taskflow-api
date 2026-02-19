from fastapi import APIRouter, HTTPException, Depends
from prisma.errors import UniqueViolationError
from app.schemas.auth import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from app.services.prisma import db
from jose import JWTError, jwt
from app.core.security import SECRET_KEY, ALGORITHM
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token
)


router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(user: UserCreate):
    try:
        new_user = await db.user.create(
            data={
                "email": user.email,
                "password": hash_password(user.password)
            }
        )
        return {"message": "User created successfully"}
    except UniqueViolationError:
        raise HTTPException(status_code=400, detail="Email already registered")


@router.post("/login")
async def login(user: UserLogin):
    db_user = await db.user.find_unique(where={"email": user.email})

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": str(db_user.id)})
    refresh_token = create_refresh_token({"sub": str(db_user.id)})

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh")
async def refresh_token(refresh_token: str):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        user_id = payload.get("sub")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token({"sub": user_id})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }