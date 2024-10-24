import pytest

from pydantic import ValidationError
from pymongo.results import InsertOneResult

from app.models.campaign_model import Campaign
from app.models.character_model import Character, CharacterCreate, CharacterUpdate
from app.models.character_sheet_model import CharacterSheet
from app.models.user_model import User
from config import Config
from bson import ObjectId
from unittest.mock import MagicMock

from app.services.character_service import CharacterService


class TestCharacterService:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.service = CharacterService()

        self.mock_campaign_service = MagicMock()
        mocker.patch.object(self.service, 'campaign_service', self.mock_campaign_service)

        self.mock_user_service = MagicMock()
        mocker.patch.object(self.service, 'user_service', self.mock_user_service)

        self.mock_collection = MagicMock()
        mocker.patch.object(self.service, 'get_db', return_value=self.mock_collection)

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

        raw_character = {
            "_id": ObjectId(_id),
            "player": player_id,
            "campaign": campaign_id,
            "player_character_sheet": {
                "fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                "attributes": {"Attribute 1": 20, "Attribute 2": 10}
            }
        }

        character = Character(
            id=_id,
            player=player_user,
            campaign=campaign,
            player_character_sheet={"fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                                    "attributes": {"Attribute 1": 20, "Attribute 2": 10}}
        )

        expected_response = {
            "_id": _id,
            "player": {'id': player_id, 'name': player_user.name, 'email': player_user.email},
            "campaign": {
                "id": campaign_id, "name": campaign.name,
                "description": campaign.description,
                "master": {"id": master_id, "name": master_user.name, "email": master_user.email},
                "player_character_sheet": {
                    "fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                    "attributes": {"Attribute 1": 20, "Attribute 2": 10}
                }
            }
        }

        return raw_character, character, expected_response

    @pytest.fixture
    def create_character_data(self):
        _id = str(ObjectId())

        character_create = CharacterCreate(
            player=str(ObjectId()),
            campaign=str(ObjectId()),
            player_character_sheet={
                "fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                "attributes": {"Attribute 1": 20, "Attribute 2": 10}
            }
        )

        expected_response = {
            "detail": "Personagem cadastrado com sucesso!", "id": _id
        }

        return _id, character_create, expected_response

    @pytest.fixture
    def update_character_data(self):
        _id = str(ObjectId())

        character_update = CharacterUpdate(
            player=str(ObjectId()),
            campaign=str(ObjectId()),
            player_character_sheet={
                "fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                "attributes": {"Attribute 1": 20, "Attribute 2": 10}
            }
        )

        updated_character = {
            '_id': ObjectId(_id),
            'player': str(ObjectId()),
            'campaign': str(ObjectId()),
            'player_character_sheet': {
                "fields": {"Field 1": "Value 1", "Field 2": "Value 2"},
                "attributes": {"Attribute 1": 20, "Attribute 2": 10}
            }
        }

        expected_response = {
            "detail": "Personagem atualizado com sucesso!", "id": _id
        }

        return _id, character_update, updated_character, expected_response

    def test_get_db_initializes_connection(self, mocker):
        service = CharacterService()

        mock_mongo_client = mocker.patch('app.services.character_service.MongoClient')

        mock_db = mock_mongo_client.return_value['RoleForge']
        mock_collection = mock_db['Characters']

        result = service.get_db()

        mock_mongo_client.assert_called_once_with(Config.MONGO_URI)
        assert result == mock_collection
        assert service.characters_collection == mock_collection

    def test_get_db_reuses_existing_connection(self, mocker):
        service = CharacterService()

        mock_collection = MagicMock()
        service.characters_collection = mock_collection

        result = service.get_db()

        assert result == mock_collection
        mocker.patch('app.services.character_service.MongoClient').assert_not_called()

    def test_get_all_characters_with_data(self, character_data):
        raw_character, character, expected_response = character_data

        self.mock_collection.find.return_value = [raw_character]
        self.mock_user_service.get_users_by_ids.return_value = [character.player]
        self.mock_campaign_service.get_campaigns_by_ids.return_value = [character.campaign]

        expected_characters = [character]

        result = self.service.get_all_characters()

        assert result == expected_characters
        self.mock_collection.find.assert_called_once()

    def test_get_all_characters_no_data(self):
        self.mock_collection.find.return_value = []

        result = self.service.get_all_characters()

        assert result == []
        self.mock_collection.find.assert_called_once()

    def test_get_characters_by_player_with_data(self, character_data):
        raw_character, character, expected_response = character_data

        self.mock_collection.find.return_value = [raw_character]
        self.mock_user_service.get_users_by_ids.return_value = [character.player]
        self.mock_campaign_service.get_campaigns_by_ids.return_value = [character.campaign]

        expected_characters = [character]

        result = self.service.get_characters_by_player(character.player.id)

        assert result == expected_characters
        self.mock_collection.find.assert_called_once()

    def test_get_characters_by_player_no_data(self):
        self.mock_collection.find.return_value = []

        result = self.service.get_characters_by_player(str(ObjectId()))

        assert result == []
        self.mock_collection.find.assert_called_once()

    def test_get_character_by_id_with_data(self, character_data):
        raw_character, character, expected_response = character_data

        self.mock_collection.find_one.return_value = raw_character
        self.mock_user_service.get_user_by_id.return_value = character.player
        self.mock_campaign_service.get_campaign_by_id.return_value = character.campaign

        expected_character = character

        result = self.service.get_character_by_id(character.id)

        assert result == expected_character
        self.mock_collection.find_one.assert_called_once()

    def test_get_character_by_id_no_data(self):
        self.mock_collection.find_one.return_value = None

        result = self.service.get_character_by_id(str(ObjectId()))

        assert result is None
        self.mock_collection.find_one.assert_called_once()

    def test_create_character(self, create_character_data):
        _id, character_create, expected_response = create_character_data

        self.mock_collection.insert_one.return_value = InsertOneResult(ObjectId(_id), acknowledged=True)

        result = self.service.create_character(character_create)

        assert result == expected_response
        self.mock_collection.insert_one.assert_called_once()

    def test_create_character_validation_error(self, mocker):
        character_mock = MagicMock()

        mocker.patch.object(character_mock, 'model_dump',
                            side_effect=ValidationError.from_exception_data("Invalid data", line_errors=[]))

        with pytest.raises(ValidationError):
            self.service.create_character(character_mock)

        self.mock_collection.insert_one.assert_not_called()

    def test_update_character_with_data(self, update_character_data):
        _id, character_update, updated_character, expected_response = update_character_data

        self.mock_collection.find_one_and_update.return_value = updated_character

        result = self.service.update_character(_id, character_update)

        assert result == expected_response
        self.mock_collection.find_one_and_update.assert_called_once()

    def test_update_character_no_data(self, update_character_data):
        _id, character_update, _, _ = update_character_data

        self.mock_collection.find_one_and_update.return_value = None

        result = self.service.update_character(_id, character_update)

        assert result is None
        self.mock_collection.find_one_and_update.assert_called_once()

    def test_delete_character(self):
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 1

        self.mock_collection.delete_one.return_value = mock_delete_result

        result = self.service.delete_character(str(ObjectId()))

        assert result is True
        self.mock_collection.delete_one.assert_called_once()

    def test_get_characters_with_players_and_campaigns(self, character_data):
        raw_character, character, expected_response = character_data

        self.mock_user_service.get_users_by_ids.return_value = [character.player]
        self.mock_campaign_service.get_campaigns_by_ids.return_value = [character.campaign]

        parameters = [raw_character]
        expected_characters = [character]

        result = self.service.get_characters_with_players_and_campaigns(parameters)

        assert result == expected_characters
