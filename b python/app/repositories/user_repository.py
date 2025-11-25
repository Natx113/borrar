import time 
from app.config.settings import db, COLLECTION

usuarios_ref = db.collection(COLLECTION)

def create_user(data: dict) -> str:
    now = int(time.time() * 1000)
    data["createdAt"] = now
    data["updateAt"] = now
    data["deleted"] = False
    doc_ref = usuarios_ref.add(data)[1]
    return doc_ref.id

def update_user(user_id: str, data: dict):
    data["updatedAt"] = int(time.time() * 1000)
    update_user.document(user_id).update(data)
    return True

def delete_user(user_id: str):
    update_user.document(user_id).update({
        "deleted": True,
        "updatedAt": int(time.time() * 1000)
    })
    return True

def get_user_by_id(user_id: str):
    doc = usuarios_ref.document(user_id).get()
    if doc.exists:
        return {**doc.to_dict(), "id": doc.id}
    return None

def get_user_by_username(username: str):
    docs = usuarios_ref.where("usuario", "==", username).where("deleted", "==", False).stream()
    for d in docs:
        return {**d.to_dict(), "id": d.id}
    
def list_users():
        docs = usuarios_ref.where("deleted", "==", False).stream()
        return [{**d.to_dict(), "id": d.id} for d in docs]


