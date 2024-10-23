import pytest

from pydantic import ValidationError
from pymongo.results import InsertOneResult
from config import Config
from bson import ObjectId
from unittest.mock import MagicMock

from app.models.user_model import User, UserUpdate, UserCreate
from app.services.user_service import UserService


class TestUserService:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.service = UserService()

        self.mock_collection = MagicMock()
        mocker.patch.object(self.service, 'get_db', return_value=self.mock_collection)

    @pytest.fixture
    def user_data(self):
        _id = str(ObjectId())

        user = User(id=_id, name="Player", email="player@email.com")

        raw_user = {
            "_id": _id,
            "name": "Player",
            "email": "player@email.com"
        }

        return user, raw_user

    @pytest.fixture
    def create_user_data(self):
        _id = str(ObjectId())

        user_create = UserCreate(name="New Player", email="player@email.com")

        expected_response = {
            "detail": "Usuário cadastrado com sucesso!",
            "id": _id
        }

        return _id, user_create, expected_response

    @pytest.fixture
    def update_user_data(self):
        _id = str(ObjectId())

        user_update = UserUpdate(name="Player", email="player@email.com")

        updated_user = {
            '_id': ObjectId(_id),
            'name': user_update.name,
            'email': user_update.email
        }

        expected_response = User(id=_id, name=user_update.name, email=user_update.email)

        return _id, user_update, updated_user, expected_response

    def test_get_db_initializes_connection(self, mocker):
        service = UserService()

        mock_mongo_client = mocker.patch('app.services.user_service.MongoClient')

        mock_db = mock_mongo_client.return_value['RoleForge']
        mock_collection = mock_db['Users']

        result = service.get_db()

        mock_mongo_client.assert_called_once_with(Config.MONGO_URI)
        assert result == mock_collection
        assert service.users_collection == mock_collection

    def test_get_db_reuses_existing_connection(self, mocker):
        service = UserService()

        mock_collection = MagicMock()
        service.users_collection = mock_collection

        result = service.get_db()

        assert result == mock_collection
        mocker.patch('app.services.user_service.MongoClient').assert_not_called()

    def test_get_all_users_with_data(self, user_data):
        user, raw_user = user_data

        self.mock_collection.find.return_value = [raw_user]

        expected_users = [user]

        result = self.service.get_all_users()

        assert result == expected_users
        self.mock_collection.find.assert_called_once()

    def test_get_all_users_no_data(self):
        self.mock_collection.find.return_value = []

        result = self.service.get_all_users()

        assert result == []
        self.mock_collection.find.assert_called_once()

    def test_get_user_by_id_with_data(self, user_data):
        user, raw_user = user_data

        self.mock_collection.find_one.return_value = raw_user

        expected_user = user

        result = self.service.get_user_by_id(user.id)

        assert result == expected_user
        self.mock_collection.find_one.assert_called_once()

    def test_get_user_by_id_no_data(self):
        self.mock_collection.find_one.return_value = None

        result = self.service.get_user_by_id(str(ObjectId()))

        assert result is None
        self.mock_collection.find_one.assert_called_once()

    def test_get_users_by_ids_with_data(self, user_data):
        user, raw_user = user_data

        self.mock_collection.find.return_value = [raw_user]

        expected_users = [user]

        result = self.service.get_users_by_ids([user.id])

        assert result == expected_users
        self.mock_collection.find.assert_called_once()

    def test_get_users_by_ids_no_data(self):
        self.mock_collection.find.return_value = None

        result = self.service.get_users_by_ids([str(ObjectId())])

        assert result is None
        self.mock_collection.find.assert_called_once()

    def test_get_user_by_email_with_data(self, user_data):
        user, raw_user = user_data

        self.mock_collection.find_one.return_value = raw_user

        expected_user = user

        result = self.service.get_user_by_email(user.email)

        assert result == expected_user
        self.mock_collection.find_one.assert_called_once()

    def test_get_user_by_email_no_data(self):
        self.mock_collection.find_one.return_value = None

        result = self.service.get_user_by_email("email@test.com")

        assert result is None
        self.mock_collection.find_one.assert_called_once()

    def test_create_user(self, create_user_data):
        _id, user_create, expected_response = create_user_data

        self.mock_collection.insert_one.return_value = InsertOneResult(ObjectId(_id), acknowledged=True)

        result = self.service.create_user(user_create)

        assert result == expected_response
        self.mock_collection.insert_one.assert_called_once()

    def test_create_user_validation_error(self, mocker):
        user_mock = MagicMock()

        mocker.patch.object(user_mock, 'model_dump',
                            side_effect=ValidationError.from_exception_data("Invalid data", line_errors=[]))

        with pytest.raises(ValidationError):
            self.service.create_user(user_mock)

        self.mock_collection.insert_one.assert_not_called()

    def test_update_user_with_data(self, update_user_data):
        _id, user_update, updated_user, expected_response = update_user_data

        self.mock_collection.find_one_and_update.return_value = updated_user

        result = self.service.update_user(_id, user_update)

        assert result == expected_response
        self.mock_collection.find_one_and_update.assert_called_once()

    def test_update_user_no_data(self, update_user_data):
        _id, user_update, _, _ = update_user_data

        self.mock_collection.find_one_and_update.return_value = None

        result = self.service.update_user(_id, user_update)

        assert result is None
        self.mock_collection.find_one_and_update.assert_called_once()

    def test_delete_user(self):
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 1

        self.mock_collection.delete_one.return_value = mock_delete_result

        result = self.service.delete_user(str(ObjectId()))

        assert result is True
        self.mock_collection.delete_one.assert_called_once()
