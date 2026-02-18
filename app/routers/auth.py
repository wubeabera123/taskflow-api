from fastapi import APIRouter, HTTPException, Depends
from prisma.errors import UniqueViolationError
from app.schemas.auth import UserCreate, UserLogin
from app.core.security import hash_password, verify_password, create_access_token
from app.services.prisma import db

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

    token = create_access_token({"sub": str(db_user.id)})

    return {
        "access_token": token,
        "token_type": "bearer"
    }
