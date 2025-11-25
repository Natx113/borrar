from fastapi import Depends, HTTPException
from app.schema.user_schema import UserLogin, UserRegister
from app.services import user_service
from app.middleware.auth import get_current_user

def register(user: UserRegister):
    user_id = user_service.register_user(user.dict())
    return {
        "ok": True,
        "id": user_id
    }

def login(data: UserLogin):
    token, user = user_service.login_user(data.usuario, data.password)
    return{
        "ok":True,
        "token": token,
        "user": user
    }

def list_users(current_user: dict = Depends(get_current_user)):
    return{
        "ok": True,
        "users": user_service.list_users()

    }

def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    return{
        "ok": True,
        "user": user_service.get_user(user_id)
    }

def update_user(user_id: str, data: dict, current_user: dict = Depends(get_current_user)):
    user_service.update_user(user_id, data)
    return{
        "ok":True
    }

def delete_user(user_id:str, current_user: dict = Depends(get_current_user)):
    user_service.delete_user(user_id)
    return{
        "ok":True
    }