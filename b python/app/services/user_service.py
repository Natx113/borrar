from fastapi import HTTPException
from app.repositories import user_repository
from app.utils.hash import hash_password, verify_password
from app.utils.jwt import create_token

def register_user(data: dict):
    if user_repository.get_user_by_username(data["usuario"]):
        raise HTTPException(status_code=4000, detail="Usuario ya existe")
    data["password"] = hash_password(data["password"])
    return user_repository.create_user(data)

def login_user(usuario: str, password:str):
    user = user_repository.get_user_by_username(usuario)
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=4000, detail="Contraseña incorrecta")
    token = create_token(user["id"], user["usuario"])
    user.pop("password", None)
    return token, user

def list_users():
    users =  user_repository.list_users()
    for u in users:
        u.pop("password", None)
    return users

def get_user(user_id: str):
    user = user_repository.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=4000, detail="Usuario no encontrado")
    user.pop("password", None)
    return user

def update_user(user_id: str, data: dict):
    if "password" in data:
        data["password"] = hash_password(data["password"])
    return user_repository.update_user(user_id, data)

def delete_user(user_id: str):
    return user_repository.delete_user(user_id)

