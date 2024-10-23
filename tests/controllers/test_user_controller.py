import pytest

from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.controllers.user_controller import UserController
from app.models.user_model import User, UserCreate, UserUpdate


class TestUserController:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.app = FastAPI()
        self.controller = UserController()

        self.app.include_router(self.controller.router, prefix="/users")
        self.client = TestClient(self.app)

        self.mock_user_service = MagicMock()
        mocker.patch.object(self.controller, 'user_service', self.mock_user_service)

    @pytest.fixture
    def user_data(self):
        _id = str(ObjectId())

        user = User(id=_id, name="Player", email="player@email.com")

        expected_response = {
            "id": _id,
            "name": "Player",
            "email": "player@email.com"
        }

        return user, expected_response

    @pytest.fixture
    def create_user_data(self):
        user_create = UserCreate(name="New Player", email="player@email.com")

        expected_response = {"detail": "Usuário cadastrado com sucesso!", "id": str(ObjectId)}

        return user_create, expected_response

    @pytest.fixture
    def update_user_data(self):
        _id = str(ObjectId())

        user_update = UserUpdate(name="Player", email="player@email.com")

        updated_user = User(id=_id, name=user_update.name, email=user_update.email)

        expected_response = {
            'id': _id,
            'name': user_update.name,
            'email': user_update.email
        }

        return _id, user_update, updated_user, expected_response

    def test_get_users_with_data(self, user_data):
        user, expected_response = user_data

        self.mock_user_service.get_all_users.return_value = [user]

        response = self.client.get("/users/")

        assert response.status_code == 200
        assert response.json() == [expected_response]
        self.mock_user_service.get_all_users.assert_called_once()

    def test_get_users_no_data(self):
        self.mock_user_service.get_all_users.return_value = []

        response = self.client.get("/users/")

        assert response.status_code == 404
        assert response.json() == {"detail": "Nenhum usuário encontrado."}
        self.mock_user_service.get_all_users.assert_called_once()

    def test_get_user_by_id_with_data(self, user_data):
        user, expected_response = user_data

        self.mock_user_service.get_user_by_id.return_value = user

        response = self.client.get(f'/users/{user.id}')

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_user_service.get_user_by_id.assert_called_once_with(user.id)

    def test_get_user_by_id_no_data(self):
        self.mock_user_service.get_user_by_id.return_value = None

        response = self.client.get(f'/users/{str(ObjectId())}')

        assert response.status_code == 404
        assert response.json() == {"detail": "Usuário não encontrado."}
        self.mock_user_service.get_user_by_id.assert_called_once()

    def test_get_user_by_email_with_data(self, user_data):
        user, expected_response = user_data

        self.mock_user_service.get_user_by_email.return_value = user

        response = self.client.get(f'/users/email/{user.email}')

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_user_service.get_user_by_email.assert_called_once_with(user.email)

    def test_get_user_by_email_no_data(self):
        self.mock_user_service.get_user_by_email.return_value = None

        response = self.client.get(f'/users/email/email@test.com')

        assert response.status_code == 404
        assert response.json() == {"detail": "Usuário não encontrado."}
        self.mock_user_service.get_user_by_email.assert_called_once()

    def test_create_user(self, create_user_data):
        user_create, expected_response = create_user_data

        self.mock_user_service.create_user.return_value = expected_response

        response = self.client.post("/users/", json=user_create.model_dump())

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_user_service.create_user.assert_called_once_with(user_create)

    def test_update_user(self, update_user_data):
        _id, user_update, updated_user, expected_response = update_user_data

        self.mock_user_service.update_user.return_value = updated_user

        response = self.client.put(f"/users/{_id}", json=user_update.model_dump())
        print('RESPOSTA: ', response.json())
        print('ESPERADO: ', expected_response)

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_user_service.update_user.assert_called_once_with(_id, user_update)

    def test_update_user_no_data(self, update_user_data):
        _id, user_update, _, _ = update_user_data

        self.mock_user_service.update_user.return_value = None

        response = self.client.put(f"/users/{_id}", json=user_update.model_dump())

        assert response.status_code == 404
        assert response.json() == {"detail": "Usuário não encontrado."}
        self.mock_user_service.update_user.assert_called_once_with(_id, user_update)

    def test_delete_user_success(self):
        _id = str(ObjectId())

        self.mock_user_service.delete_user.return_value = True

        response = self.client.delete(f"/users/{_id}")

        assert response.status_code == 200
        assert response.json() == {"message": "Usuário excluído com sucesso."}
        self.mock_user_service.delete_user.assert_called_once_with(_id)

    def test_delete_user_not_found(self):
        _id = str(ObjectId())

        self.mock_user_service.delete_user.return_value = False

        response = self.client.delete(f"/users/{_id}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Usuário não encontrado."}
        self.mock_user_service.delete_user.assert_called_once_with(_id)
