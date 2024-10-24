import pytest

from pydantic import ValidationError
from pymongo.results import InsertOneResult
from config import Config
from bson import ObjectId
from unittest.mock import MagicMock

from app.models.character_sheet_model import CharacterSheet
from app.models.user_model import User
from app.services.campaign_service import CampaignService
from app.models.campaign_model import Campaign, CampaignCreate, CampaignUpdate


class TestCampaignService:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.service = CampaignService()

        self.mock_user_service = MagicMock()
        mocker.patch.object(self.service, 'user_service', self.mock_user_service)

        self.mock_collection = MagicMock()
        mocker.patch.object(self.service, 'get_db', return_value=self.mock_collection)

    @pytest.fixture
    def campaign_data(self):
        _id = str(ObjectId())
        master_id = str(ObjectId())
        master_user = User(id=master_id, name="Master 1", email="master1@email.com")
        player_id = str(ObjectId())
        player_user = User(id=player_id, name="Player", email="player@email.com")

        raw_campaign = {
            '_id': ObjectId(_id),
            'name': 'Campaign 1',
            'description': 'First campaign',
            'master': master_id,
            'players': [player_id],
            'character_sheet': {'fields': ['Field 1', 'Field 2'], 'attributes': ['Attribute 1', 'Attribute 2']}
        }

        campaign = Campaign(
            id=_id,
            name='Campaign 1',
            description='First campaign',
            master=master_user,
            players=[player_user],
            character_sheet=CharacterSheet(fields=["Field 1", "Field 2"], attributes=["Attribute 1", "Attribute 2"])
        )

        expected_response = {
            'id': _id,
            'name': 'Campaign 1',
            'description': 'First campaign',
            'master': {'id': master_id, 'name': 'Master 1', 'email': 'master1@email.com'},
            'players': [{'id': player_id, 'name': 'Player', 'email': 'player@email.com'}],
            'character_sheet': {'fields': ['Field 1', 'Field 2'], 'attributes': ['Attribute 1', 'Attribute 2']}
        }

        return raw_campaign, campaign, expected_response

    @pytest.fixture
    def create_campaign_data(self):
        _id = str(ObjectId())

        campaign_create = CampaignCreate(
            name="New Campaign",
            description="A New Campaign",
            master=str(ObjectId()),
            players=[str(ObjectId()), str(ObjectId())],
            character_sheet=CharacterSheet(fields=["Field 1", "Field 2"],
                                           attributes=["Attribute 1", "Attribute 2"])
        )

        expected_response = {
            "detail": "Campanha cadastrada com sucesso!",
            "id": _id
        }

        return _id, campaign_create, expected_response

    @pytest.fixture
    def update_campaign_data(self):
        _id = str(ObjectId())

        campaign_update = CampaignUpdate(
            name="Updated Campaign",
            description="This is an updated description",
            master=str(ObjectId()),
            players=[str(ObjectId())],
            character_sheet=CharacterSheet(fields=["Field 1", "Field 2"], attributes=["Attribute 1", "Attribute 2"])
        )

        updated_campaign = {
            '_id': ObjectId(_id),
            'name': campaign_update.name,
            'description': campaign_update.description,
            'master': ObjectId(campaign_update.master),
            'players': [ObjectId(campaign_update.players[0])],
            'character_sheet': {'fields': ['PV', 'PE', 'Sanidade'], 'attributes': ['Intelecto', 'Vigor', 'Presença']}}

        expected_response = {
            "detail": "Campanha atualizada com sucesso!",
            "id": _id
        }

        return _id, campaign_update, updated_campaign, expected_response

    def test_get_db_initializes_connection(self, mocker):
        service = CampaignService()

        mock_mongo_client = mocker.patch('app.services.campaign_service.MongoClient')

        mock_db = mock_mongo_client.return_value['RoleForge']
        mock_collection = mock_db['Campaigns']

        result = service.get_db()

        mock_mongo_client.assert_called_once_with(Config.MONGO_URI)
        assert result == mock_collection
        assert service.campaigns_collection == mock_collection

    def test_get_db_reuses_existing_connection(self, mocker):
        service = CampaignService()

        mock_collection = MagicMock()
        service.campaigns_collection = mock_collection

        result = service.get_db()

        assert result == mock_collection
        mocker.patch('app.services.campaign_service.MongoClient').assert_not_called()

    def test_get_all_campaigns_with_data(self, campaign_data):
        raw_campaign, campaign, expected_response = campaign_data

        self.mock_collection.find.return_value = [raw_campaign]

        self.mock_user_service.get_users_by_ids.return_value = [campaign.master, campaign.players[0]]

        expected_campaigns = [campaign]

        result = self.service.get_all_campaigns()

        assert result == expected_campaigns
        self.mock_collection.find.assert_called_once()

    def test_get_all_campaigns_no_data(self):
        self.mock_collection.find.return_value = []

        result = self.service.get_all_campaigns()

        assert result == []
        self.mock_collection.find.assert_called_once()

    def test_get_campaigns_by_master_with_data(self, campaign_data):
        raw_campaign, campaign, expected_response = campaign_data

        self.mock_collection.find.return_value = [raw_campaign]
        self.mock_user_service.get_users_by_ids.return_value = [campaign.master, campaign.players[0]]

        expected_campaigns = [campaign]

        result = self.service.get_campaigns_by_master(campaign.master.id)

        assert result == expected_campaigns
        self.mock_collection.find.assert_called_once()

    def test_get_campaigns_by_master_no_data(self):
        self.mock_collection.find.return_value = []

        result = self.service.get_campaigns_by_master(str(ObjectId()))

        assert result == []
        self.mock_collection.find.assert_called_once()

    def test_get_campaigns_by_player_with_data(self, campaign_data):
        raw_campaign, campaign, expected_response = campaign_data

        self.mock_collection.find.return_value = [raw_campaign]
        self.mock_user_service.get_users_by_ids.return_value = [campaign.master, campaign.players[0]]

        expected_campaigns = [campaign]

        result = self.service.get_campaigns_by_player(campaign.players[0].id)

        assert result == expected_campaigns
        self.mock_collection.find.assert_called_once()

    def test_get_campaigns_by_player_no_data(self):
        self.mock_collection.find.return_value = []

        result = self.service.get_campaigns_by_player(str(ObjectId()))

        assert result == []
        self.mock_collection.find.assert_called_once()

    def test_get_campaign_by_id_with_data(self, campaign_data):
        raw_campaign, campaign, expected_response = campaign_data

        self.mock_collection.find_one.return_value = raw_campaign
        self.mock_user_service.get_user_by_id.return_value = campaign.master
        self.mock_user_service.get_users_by_ids.return_value = campaign.players

        expected_campaign = campaign

        result = self.service.get_campaign_by_id(campaign.id)

        assert result == expected_campaign
        self.mock_collection.find_one.assert_called_once()

    def test_get_campaign_by_id_no_data(self):
        self.mock_collection.find_one.return_value = None

        result = self.service.get_campaign_by_id(str(ObjectId()))

        assert result is None
        self.mock_collection.find_one.assert_called_once()

    def test_get_campaigns_by_ids_with_data(self, campaign_data):
        raw_campaign, campaign, expected_response = campaign_data

        self.mock_collection.find.return_value = [raw_campaign]
        self.mock_user_service.get_users_by_ids.return_value = [campaign.master, campaign.players[0]]

        expected_campaigns = [campaign]

        result = self.service.get_campaigns_by_ids([campaign.id])

        assert result == expected_campaigns
        self.mock_collection.find.assert_called_once()

    def test_get_campaigns_by_ids_no_data(self):
        self.mock_collection.find.return_value = []

        result = self.service.get_campaigns_by_ids([str(ObjectId())])

        assert result == []
        self.mock_collection.find.assert_called_once()

    def test_create_campaign(self, create_campaign_data):
        _id, campaign_create, expected_response = create_campaign_data

        self.mock_collection.insert_one.return_value = InsertOneResult(ObjectId(_id), acknowledged=True)

        result = self.service.create_campaign(campaign_create)

        assert result == expected_response
        self.mock_collection.insert_one.assert_called_once()

    def test_create_campaign_validation_error(self, mocker):
        campaign_mock = MagicMock()

        mocker.patch.object(campaign_mock, 'model_dump',
                            side_effect=ValidationError.from_exception_data("Invalid data", line_errors=[]))

        with pytest.raises(ValidationError):
            self.service.create_campaign(campaign_mock)

        self.mock_collection.insert_one.assert_not_called()

    def test_update_campaign_with_data(self, update_campaign_data):
        _id, campaign_update, updated_campaign, expected_response = update_campaign_data

        self.mock_collection.find_one_and_update.return_value = updated_campaign

        result = self.service.update_campaign(_id, campaign_update)

        assert result == expected_response
        self.mock_collection.find_one_and_update.assert_called_once()

    def test_update_campaign_no_data(self, update_campaign_data):
        _id, campaign_update, _, _ = update_campaign_data

        self.mock_collection.find_one_and_update.return_value = None

        result = self.service.update_campaign(_id, campaign_update)

        assert result is None
        self.mock_collection.find_one_and_update.assert_called_once()

    def test_delete_campaign(self):
        mock_delete_result = MagicMock()
        mock_delete_result.deleted_count = 1

        self.mock_collection.delete_one.return_value = mock_delete_result

        result = self.service.delete_campaign(str(ObjectId()))

        assert result is True
        self.mock_collection.delete_one.assert_called_once()

    def test_get_campaigns_with_users(self, campaign_data):
        raw_campaign, campaign, _ = campaign_data

        self.mock_user_service.get_users_by_ids.return_value = [campaign.master, campaign.players[0]]

        parameters = [raw_campaign]
        expected_campaigns = [campaign]

        result = self.service.get_campaigns_with_users(parameters)

        assert result == expected_campaigns
