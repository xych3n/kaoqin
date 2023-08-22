from fastapi import APIRouter

from . import activities, login, users, particips


api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(activities.router, prefix="/activities", tags=["activities"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(particips.router, prefix="/particips", tags=["particips"])
