from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from db.db import get_user, create_user, login_user

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

user_router = APIRouter()


@user_router.get("/{user_id}")
async def get_user_h(user_id: int):
    user = await get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


class RegUsr(BaseModel):
    email: str
    password: str
    name: str

    class Config:
        arbitrary_types_allowed = True


@user_router.post("/registration")
async def create_user_h(data: RegUsr):
    user = data.dict()
    user_id = await create_user(user["email"], user["password"], user["name"])
    if user_id is None:
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return user_id[0]


class LogUsr(BaseModel):
    email: str
    password: str

    class Config:
        arbitrary_types_allowed = True


@user_router.post("/login")
async def login_user_h(data: LogUsr):
    data = data.dict()
    user_id = await login_user(data["email"], data["password"])
    if user_id is None:
        raise HTTPException(status_code=404, detail="Invalid login or password")
    return user_id


app.include_router(user_router, prefix="/user", tags=["user"])
