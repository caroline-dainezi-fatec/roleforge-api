from fastapi import APIRouter, HTTPException
from typing import List

from app.models.user_model import User, UserCreate, UserUpdate
from app.services.user_service import UserService


class UserController:
    def __init__(self):
        self.router = APIRouter()
        self.user_service = UserService()
        self.register_routes()

    def register_routes(self):
        self.router.get("/", response_model=List[User])(self.get_users)
        self.router.get("/{user_id}", response_model=User)(self.get_user_by_id)
        self.router.get("/email/{user_email}", response_model=User)(self.get_user_by_email)
        self.router.post("/", response_model=dict[str, str])(self.create_user)
        self.router.put("/{user_id}", response_model=User)(self.update_user)
        self.router.delete("/{user_id}", response_model=dict)(self.delete_user)

    def get_users(self):
        users = self.user_service.get_all_users()
        if not users:
            raise HTTPException(status_code=404, detail="Nenhum usuário encontrado.")
        return users

    def get_user_by_id(self, user_id: str):
        user = self.user_service.get_user_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return user

    def get_user_by_email(self, user_email: str):
        user = self.user_service.get_user_by_email(user_email)
        if user is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return user

    def create_user(self, user: UserCreate):
        return self.user_service.create_user(user)

    def update_user(self, user_id: str, user: UserUpdate):
        updated_user = self.user_service.update_user(user_id, user)
        if updated_user is None:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return updated_user

    def delete_user(self, user_id: str):
        if not self.user_service.delete_user(user_id):
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        return {"message": "Usuário excluído com sucesso."}
