from fastapi import APIRouter
from app.controllers import user_controller
from app.schema.user_schema import UserLogin, UserRegister

router = APIRouter()

#Rutas Publicas
router.post("/auth/register")(user_controller.register)
router.post("/auth/login")(user_controller.login)

#Rutas Protegidas
router.get("/usuarios")(user_controller.list_users)
router.get("/usuarios/{user_id}")(user_controller.get_user)
router.put("/usuarios/{user_id}")(user_controller.update_user)
router.delete("/usuarios/{user_id}")(user_controller.delete_user)