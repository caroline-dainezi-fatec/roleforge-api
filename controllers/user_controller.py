from fastapi import APIRouter, HTTPException
from typing import List
from models.user_model import User, UserCreate, UserUpdate
from services.user_service import UserService

router = APIRouter()
user_service = UserService()


@router.get("/", response_model=List[User])
def get_users():
    return user_service.get_all_users()


@router.get("/{user_id}", response_model=User)
def get_user_by_id(user_id: str):
    user = user_service.get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return user


@router.get("/email/{user_email}", response_model=User)
def get_user_by_email(user_email: str):
    user = user_service.get_user_by_email(user_email)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return user


@router.post("/", response_model=User)
def create_user(user: UserCreate):
    return user_service.create_user(user)


@router.put("/{user_id}", response_model=User)
def update_user(user_id: str, user: UserUpdate):
    updated_user = user_service.update_user(user_id, user)
    if updated_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return updated_user


@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: str):
    if not user_service.delete_user(user_id):
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return {"message": "Usuário excluído com sucesso."}
