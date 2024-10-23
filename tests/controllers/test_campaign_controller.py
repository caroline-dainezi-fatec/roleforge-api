import pytest

from bson import ObjectId
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import MagicMock

from app.controllers.campaign_controller import CampaignController
from app.models.character_sheet_model import CharacterSheet
from app.models.user_model import User
from app.models.campaign_model import Campaign, CampaignCreate, CampaignUpdate


class TestCampaignController:
    @pytest.fixture(autouse=True)
    def setup(self, mocker):
        self.app = FastAPI()
        self.controller = CampaignController()

        self.app.include_router(self.controller.router, prefix="/campaigns")
        self.client = TestClient(self.app)

        self.mock_campaign_service = MagicMock()
        mocker.patch.object(self.controller, 'campaign_service', self.mock_campaign_service)

        self.mock_user_service = MagicMock()
        mocker.patch.object(self.controller, 'user_service', self.mock_user_service)

    @pytest.fixture
    def campaign_data(self):
        _id = str(ObjectId())
        master_id = str(ObjectId())

        campaign = Campaign(
            id=_id,
            name='Campaign 1',
            description='First campaign',
            master=User(id=master_id, name="Master 1", email="master1@email.com"),
            players=[],
            character_sheet=CharacterSheet(fields=["Field 1", "Field 2"], attributes=["Attribute 1", "Attribute 2"])
        )

        expected_response = {
            'id': _id,
            'name': 'Campaign 1',
            'description': 'First campaign',
            'master': {'id': master_id, 'name': 'Master 1', 'email': 'master1@email.com'},
            'players': [],
            'character_sheet': {'fields': ['Field 1', 'Field 2'], 'attributes': ['Attribute 1', 'Attribute 2']}
        }

        return campaign, expected_response

    @pytest.fixture
    def create_campaign_data(self):
        campaign_create = CampaignCreate(
            name="New Campaign",
            description="A New Campaign",
            master=str(ObjectId()),
            players=[str(ObjectId()), str(ObjectId())],
            character_sheet=CharacterSheet(fields=["Field 1", "Field 2"], attributes=["Attribute 1", "Attribute 2"])
        )

        expected_response = {
            "detail": "Campanha cadastrada com sucesso!",
            "id": str(ObjectId())
        }

        return campaign_create, expected_response

    @pytest.fixture
    def update_campaign_data(self):
        campaign_update = CampaignUpdate(
            name="Updated Campaign",
            description="This is an updated description",
            master=str(ObjectId()),
            players=[str(ObjectId())],
            character_sheet=CharacterSheet(fields=["Field 1", "Field 2"], attributes=["Attribute 1", "Attribute 2"])
        )

        expected_response = {
            "detail": "Campanha atualizada com sucesso!",
            "id": str(ObjectId())
        }

        return campaign_update, expected_response

    def test_get_campaigns_with_data(self, campaign_data):
        campaign, expected_response = campaign_data

        self.mock_campaign_service.get_all_campaigns.return_value = [campaign]

        response = self.client.get("/campaigns/")

        assert response.status_code == 200
        assert response.json() == [expected_response]
        self.mock_campaign_service.get_all_campaigns.assert_called_once()

    def test_get_campaigns_no_data(self):
        self.mock_campaign_service.get_all_campaigns.return_value = []

        response = self.client.get("/campaigns/")

        assert response.status_code == 404
        assert response.json() == {"detail": "Nenhuma campanha encontrada."}
        self.mock_campaign_service.get_all_campaigns.assert_called_once()

    def test_get_campaigns_by_master_with_data(self, campaign_data):
        campaign, expected_response = campaign_data

        self.mock_campaign_service.get_campaigns_by_master.return_value = [campaign]

        response = self.client.get(f'/campaigns/master/{str(ObjectId())}')

        assert response.status_code == 200
        assert response.json() == [expected_response]
        self.mock_campaign_service.get_campaigns_by_master.assert_called_once()

    def test_get_campaigns_by_master_no_data(self):
        self.mock_campaign_service.get_campaigns_by_master.return_value = []

        response = self.client.get(f'/campaigns/master/{str(ObjectId())}')

        assert response.status_code == 404
        assert response.json() == {"detail": "Este usuário não possui campanhas."}
        self.mock_campaign_service.get_campaigns_by_master.assert_called_once()

    def test_get_campaigns_by_player_with_data(self, campaign_data):
        campaign, expected_response = campaign_data

        self.mock_campaign_service.get_campaigns_by_player.return_value = [campaign]

        response = self.client.get(f'/campaigns/player/{str(ObjectId())}')

        assert response.status_code == 200
        assert response.json() == [expected_response]
        self.mock_campaign_service.get_campaigns_by_player.assert_called_once()

    def test_get_campaigns_by_player_no_data(self):
        self.mock_campaign_service.get_campaigns_by_player.return_value = []

        response = self.client.get(f'/campaigns/player/{str(ObjectId())}')

        assert response.status_code == 404
        assert response.json() == {"detail": "Este usuário não participa de nenhuma campanha."}
        self.mock_campaign_service.get_campaigns_by_player.assert_called_once()

    def test_get_campaign_by_id_with_data(self, campaign_data):
        campaign, expected_response = campaign_data

        self.mock_campaign_service.get_campaign_by_id.return_value = campaign

        response = self.client.get(f'/campaigns/{campaign.id}')

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_campaign_service.get_campaign_by_id.assert_called_once_with(campaign.id)

    def test_get_campaign_by_id_no_data(self):
        self.mock_campaign_service.get_campaign_by_id.return_value = None

        response = self.client.get(f'/campaigns/{str(ObjectId())}')

        assert response.status_code == 404
        assert response.json() == {"detail": "Campanha não encontrada."}
        self.mock_campaign_service.get_campaign_by_id.assert_called_once()

    def test_create_campaign(self, create_campaign_data):
        campaign_create, expected_response = create_campaign_data

        self.mock_user_service.get_user_by_id.return_value = MagicMock()
        self.mock_user_service.get_users_by_ids.return_value = [MagicMock() for _ in campaign_create.players]
        self.mock_campaign_service.create_campaign.return_value = expected_response

        response = self.client.post("/campaigns/", json=campaign_create.model_dump())

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_user_service.get_user_by_id.assert_called_once_with(campaign_create.master)
        self.mock_user_service.get_users_by_ids.assert_called_once_with(campaign_create.players)
        self.mock_campaign_service.create_campaign.assert_called_once_with(campaign_create)

    def test_create_campaign_master_not_found(self, create_campaign_data):
        campaign_create, _ = create_campaign_data

        self.mock_user_service.get_user_by_id.return_value = None

        response = self.client.post("/campaigns/", json=campaign_create.model_dump())

        assert response.status_code == 400
        assert response.json() == {"detail": "O mestre dessa campanha não foi encontrado."}
        self.mock_user_service.get_user_by_id.assert_called_once_with(campaign_create.master)

    def test_create_campaign_players_not_found(self, create_campaign_data):
        campaign_create, _ = create_campaign_data

        self.mock_user_service.get_user_by_id.return_value = MagicMock()
        self.mock_user_service.get_users_by_ids.return_value = []

        response = self.client.post("/campaigns/", json=campaign_create.model_dump())

        assert response.status_code == 400
        assert response.json() == {"detail": "Um ou mais jogadores dessa campanha não foram encontrados."}
        self.mock_user_service.get_user_by_id.assert_called_once_with(campaign_create.master)
        self.mock_user_service.get_users_by_ids.assert_called_once_with(campaign_create.players)

    def test_update_campaign(self, update_campaign_data):
        _id = str(ObjectId())
        campaign_update, expected_response = update_campaign_data

        self.mock_campaign_service.update_campaign.return_value = expected_response

        response = self.client.put(f"/campaigns/{_id}", json=campaign_update.model_dump())

        assert response.status_code == 200
        assert response.json() == expected_response
        self.mock_campaign_service.update_campaign.assert_called_once_with(_id, campaign_update)

    def test_update_campaign_no_data(self, update_campaign_data):
        _id = str(ObjectId())
        campaign_update, _ = update_campaign_data

        self.mock_campaign_service.update_campaign.return_value = None

        response = self.client.put(f"/campaigns/{_id}", json=campaign_update.model_dump())

        assert response.status_code == 404
        assert response.json() == {"detail": "Campanha não encontrada."}
        self.mock_campaign_service.update_campaign.assert_called_once_with(_id, campaign_update)

    def test_delete_campaign_success(self):
        _id = str(ObjectId())

        self.mock_campaign_service.delete_campaign.return_value = True

        response = self.client.delete(f"/campaigns/{_id}")

        assert response.status_code == 200
        assert response.json() == {"message": "Campanha excluída com sucesso."}
        self.mock_campaign_service.delete_campaign.assert_called_once_with(_id)

    def test_delete_campaign_not_found(self):
        _id = str(ObjectId())

        self.mock_campaign_service.delete_campaign.return_value = False

        response = self.client.delete(f"/campaigns/{_id}")

        assert response.status_code == 404
        assert response.json() == {"detail": "Campanha não encontrada."}
        self.mock_campaign_service.delete_campaign.assert_called_once_with(_id)
