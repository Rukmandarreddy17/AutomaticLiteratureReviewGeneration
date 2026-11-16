from fastapi import APIRouter
from app.api.v1.endpoints import auth, research, chat

api_router = APIRouter()
api_router.include_router(auth.router, tags=["login"])
api_router.include_router(research.router, prefix="/research", tags=["research"])
api_router.include_router(chat.router, prefix="/chats", tags=["chats"])
