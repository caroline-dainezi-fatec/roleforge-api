import pytest

from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.controllers.character_controller import CharacterController
from app.models.campaign_model import Campaign
from app.models.character_model import Character, CharacterCreate, CharacterUpdate
from app.models.character_sheet_model import CharacterSheet
from app.models.user_model import User


class TestCharacterController:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.app = FastAPI()
        self.controller = CharacterController()

        self.app.include_router(self.controller.router, prefix="/characters")
        self.client = TestClient(self.app)

        self.mock_character_service = MagicMock()
        mocker.patch.object(self.controller, 'character_service', self.mock_character_service)

        self.mock_campaign_service = MagicMock()
        mocker.patch.object(self.controller, 'campaign_service', self.mock_campaign_service)

        self.mock_user_service = MagicMock()
        mocker.patch.object(self.controller, 'user_service', self.mock_user_service)

    @pytest.fixture
    def character_data(self):
        _id = str(ObjectId())
        master_id = str(ObjectId())
        master_user = User(id=master_id, name="Master 1", email="master1@email.com")
        player_id = str(ObjectId())
        player_user = User(id=player_id, name="Player", email="player@email.com")
        campaign_id = str(ObjectId())
        campaign = Campaign(
            id=campaign_id,
            name='Campaign 1',
            description='First campaign',
            master=master_user,
            players=[player_user],
            character_sheet=CharacterSheet(fields=["Field 1", "Field 2"], attributes=["Attribute 1", "Attribute 2"])
        )

        character = Character(
            id=_id,
            player=player_user,
            campaign=campaign,
            player_character_sheet={"fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                                    "attributes": {"Attribute 1": 20, "Attribute 2": 10}}
        )

        expected_response = {
            "id": _id,
            "player": {"id": player_id, "name": player_user.name, "email": player_user.email},
            "campaign": {
                "id": campaign_id,
                "name": campaign.name,
                "description": campaign.description,
                "master": {"id": master_id, "name": master_user.name, "email": master_user.email},
                "players": [{"id": player_id, "name": player_user.name, "email": player_user.email}],
                "character_sheet": {"fields": ["Field 1", "Field 2"], "attributes": ["Attribute 1", "Attribute 2"]}
            },
            "player_character_sheet": {
                "fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                "attributes": {"Attribute 1": 20, "Attribute 2": 10}
            }
        }

        return character, expected_response

    @pytest.fixture
    def create_character_data(self):
        character_create = CharacterCreate(
            player=str(ObjectId()),
            campaign=str(ObjectId()),
            player_character_sheet={
                "fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                "attributes": {"Attribute 1": 20, "Attribute 2": 10}
            }
        )

        expected_response = {
            "detail": "Personagem cadastrado com sucesso!", "id": str(ObjectId())
        }

        return character_create, expected_response

    @pytest.fixture
    def update_character_data(self):
        character_update = CharacterUpdate(
            player=str(ObjectId()),
            campaign=str(ObjectId()),
            player_character_sheet={
                "fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                "attributes": {"Attribute 1": 20, "Attribute 2": 10}
            }
        )

        expected_response = {
            "detail": "Personagem atualizado com sucesso!", "id": str(ObjectId())
        }

        return character_update, expected_response

    def test_get_characters_with_data(self, character_data):
        character, expected_response = character_data

        self.mock_character_service.get_all_characters.return_value = [character]

        response = self.client.get("/characters/")

        assert response.status_code == 200
        assert response.json() == [expected_response]
        self.mock_character_service.get_all_characters.assert_called_once()

    def test_get_characters_no_data(self):
        self.mock_character_service.get_all_characters.return_value = []

        response = self.client.get("/characters/")

        assert response.status_code == 404
        assert response.json() == {"detail": "Nenhum personagem encontrado."}
        self.mock_character_service.get_all_characters.assert_called_once()

    def test_get_character_by_id_with_data(self, character_data):
        character, expected_response = character_data

        self.mock_character_service.get_character_by_id.return_value = character

        response = self.client.get(f'/characters/{character.id}')

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_character_service.get_character_by_id.assert_called_once_with(character.id)

    def test_get_character_by_id_no_data(self):
        self.mock_character_service.get_character_by_id.return_value = None

        response = self.client.get(f'/characters/{str(ObjectId())}')

        assert response.status_code == 404
        assert response.json() == {"detail": "Personagem não encontrado."}
        self.mock_character_service.get_character_by_id.assert_called_once()

    def test_get_characters_by_player_with_data(self, character_data):
        character, expected_response = character_data

        self.mock_character_service.get_characters_by_player.return_value = [character]

        response = self.client.get(f'/characters/player/{character.player.id}')

        assert response.status_code == 200
        assert response.json() == [expected_response]
        self.mock_character_service.get_characters_by_player.assert_called_once()

    def test_get_characters_by_player_no_data(self):
        self.mock_character_service.get_characters_by_player.return_value = []

        response = self.client.get(f'/characters/player/{str(ObjectId())}')

        assert response.status_code == 404
        assert response.json() == {"detail": "Este usuário não possui personagens."}
        self.mock_character_service.get_characters_by_player.assert_called_once()

    def test_create_character(self, create_character_data):
        character_create, expected_response = create_character_data

        self.mock_user_service.get_user_by_id.return_value = MagicMock()
        self.mock_campaign_service.get_campaign_by_id.return_value = MagicMock()
        self.mock_character_service.create_character.return_value = expected_response

        response = self.client.post("/characters/", json=character_create.model_dump())

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_user_service.get_user_by_id.assert_called_once_with(character_create.player)
        self.mock_campaign_service.get_campaign_by_id.assert_called_once_with(character_create.campaign)
        self.mock_character_service.create_character.assert_called_once_with(character_create)

    def test_create_character_player_not_found(self, create_character_data):
        character_create, _ = create_character_data

        self.mock_user_service.get_user_by_id.return_value = None

        response = self.client.post("/characters/", json=character_create.model_dump())

        assert response.status_code == 400
        assert response.json() == {"detail": "O jogador desse personagem não foi encontrado."}
        self.mock_user_service.get_user_by_id.assert_called_once_with(character_create.player)

    def test_create_character_campaign_not_found(self, create_character_data):
        character_create, _ = create_character_data

        self.mock_user_service.get_user_by_id.return_value = MagicMock()
        self.mock_campaign_service.get_campaign_by_id.return_value = None

        response = self.client.post("/characters/", json=character_create.model_dump())

        assert response.status_code == 400
        assert response.json() == {"detail": "A campanha desse personagem não foi encontrada."}
        self.mock_user_service.get_user_by_id.assert_called_once_with(character_create.player)
        self.mock_campaign_service.get_campaign_by_id.assert_called_once_with(character_create.campaign)

    def test_update_character(self, update_character_data):
        _id = str(ObjectId())
        character_update, expected_response = update_character_data

        self.mock_character_service.update_character.return_value = expected_response

        response = self.client.put(f"/characters/{_id}", json=character_update.model_dump())

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_character_service.update_character.assert_called_once_with(_id, character_update)

    def test_update_character_no_data(self, update_character_data):
        _id = str(ObjectId())
        character_update, _ = update_character_data

        self.mock_character_service.update_character.return_value = None

        response = self.client.put(f"/characters/{_id}", json=character_update.model_dump())

        assert response.status_code == 404
        assert response.json() == {"detail": "Personagem não encontrado."}
        self.mock_character_service.update_character.assert_called_once_with(_id, character_update)

    def test_delete_character_success(self):
        _id = str(ObjectId())

        self.mock_character_service.delete_character.return_value = True

        response = self.client.delete(f"/characters/{_id}")

        assert response.status_code == 200
        assert response.json() == {"message": "Personagem excluído com sucesso."}
        self.mock_character_service.delete_character.assert_called_once_with(_id)

    def test_delete_character_not_found(self):
        _id = str(ObjectId())

        self.mock_character_service.delete_character.return_value = False

        response = self.client.delete(f"/characters/{_id}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Personagem não encontrado."}
        self.mock_character_service.delete_character.assert_called_once_with(_id)
