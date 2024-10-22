from pymongo import MongoClient
from bson import ObjectId
from typing import List
from pydantic import ValidationError
from config import Config
from app.models.user_model import User, UserCreate, UserUpdate


class UserService:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client['RoleForge']
        self.users_collection = self.db['Users']

    def get_all_users(self) -> List[User]:
        users = self.users_collection.find()
        return [User(id=str(user['_id']), name=user['name'], email=user['email']) for user in users]

    def get_user_by_id(self, user_id: str) -> User:
        user = self.users_collection.find_one({'_id': ObjectId(user_id)})
        if user is None:
            return None
        return User(id=str(user['_id']), name=user['name'], email=user['email'])

    def get_users_by_ids(self, user_ids: List[str]) -> List[User]:
        user_object_ids = list(map(ObjectId, user_ids))
        users = self.users_collection.find({'_id': {"$in": user_object_ids}})
        if users is None:
            return None
        return [User(id=str(user['_id']), name=user['name'], email=user['email']) for user in users]

    def get_user_by_email(self, user_email: str) -> User:
        user = self.users_collection.find_one({'email': user_email})
        if user is None:
            return None
        return User(id=str(user['_id']), name=user['name'], email=user['email'])

    def create_user(self, user: UserCreate) -> dict[str, str] | None:
        try:
            new_user = user.model_dump()
            result = self.users_collection.insert_one(new_user)
            return {"detail": "Usuário cadastrado com sucesso!", "id": str(result.inserted_id)}
        except ValidationError as e:
            print(f"Validation Error: {e}")
            return None

    def update_user(self, user_id: str, user: UserUpdate) -> User:
        update_data = {k: v for k, v in user.model_dump().items() if v is not None}
        updated_user = self.users_collection.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': update_data},
            return_document=True
        )
        if updated_user is None:
            return None
        return User(id=str(updated_user['_id']), name=updated_user['name'], email=updated_user['email'])

    def delete_user(self, user_id: str) -> bool:
        result = self.users_collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0
