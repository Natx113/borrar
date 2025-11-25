from fastapi import FastAPI
from app.routes import user_routes

app = FastAPI(title="Backend con Python")

@app.get("/")
def root():
    return{
        "message": "Servidor Funcionando"
    }

app.include_router(user_routes.router, prefix="/api/v1")#con este prefijo reacciona a las demas rustas


