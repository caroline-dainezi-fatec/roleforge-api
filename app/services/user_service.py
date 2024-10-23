from pymongo import MongoClient
from bson import ObjectId
from typing import List
from pydantic import ValidationError
from config import Config

from app.models.user_model import User, UserCreate, UserUpdate


class UserService:
    def __init__(self):
        self.client = None
        self.db = None
        self.users_collection = None

    def get_db(self):
        if self.users_collection is None:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client['RoleForge']
            self.users_collection = self.db['Users']
        return self.users_collection

    def get_all_users(self) -> List[User] | None:
        users_collection = self.get_db()
        users = users_collection.find()

        if not users:
            return []
        return [User(id=str(user['_id']), name=user['name'], email=user['email']) for user in users]

    def get_user_by_id(self, user_id: str) -> User | None:
        users_collection = self.get_db()
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if user is None:
            return None
        return User(id=str(user['_id']), name=user['name'], email=user['email'])

    def get_users_by_ids(self, user_ids: List[str]) -> List[User] | None:
        users_collection = self.get_db()
        user_object_ids = list(map(ObjectId, user_ids))
        users = users_collection.find({'_id': {"$in": user_object_ids}})

        if users is None:
            return None
        return [User(id=str(user['_id']), name=user['name'], email=user['email']) for user in users]

    def get_user_by_email(self, user_email: str) -> User | None:
        users_collection = self.get_db()
        user = users_collection.find_one({'email': user_email})
        if user is None:
            return None
        return User(id=str(user['_id']), name=user['name'], email=user['email'])

    def create_user(self, user: UserCreate) -> dict[str, str] | None:
        users_collection = self.get_db()

        try:
            new_user = user.model_dump()
            result = users_collection.insert_one(new_user)
            return {"detail": "Usuário cadastrado com sucesso!", "id": str(result.inserted_id)}
        except ValidationError as e:
            print(f"Validation Error: {e}")
            raise

    def update_user(self, user_id: str, user: UserUpdate) -> User | None:
        users_collection = self.get_db()

        update_data = {k: v for k, v in user.model_dump().items() if v is not None}
        updated_user = users_collection.find_one_and_update(
            {'_id': ObjectId(user_id)},
            {'$set': update_data},
            return_document=True
        )

        if updated_user is None:
            return None
        return User(id=str(updated_user['_id']), name=updated_user['name'], email=updated_user['email'])

    def delete_user(self, user_id: str) -> bool:
        users_collection = self.get_db()
        result = users_collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0
