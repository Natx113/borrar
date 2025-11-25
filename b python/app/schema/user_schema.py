from typing import Optional
from pydantic import BaseModel, EmailStr
#en el esquema se define los datos 
class UserRegister(BaseModel):
    nombre: str
    apaterno: str
    amaterno: str
    direccion: str
    telefono: str
    ciudad: str
    estado: str
    email: str
    usuario: str
    password: str

class UserLogin(BaseModel):
    usuario: str
    password: str

class UserOut(BaseModel):
    id: str
    nombre: str
    apaterno: str
    amaterno: str
    direccion: str
    telefono: str
    ciudad: str
    estado: str
    email: str
    usuario: str