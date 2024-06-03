from pymongo import MongoClient
from bson import ObjectId
from typing import List, Dict
from pydantic import ValidationError
from config import Config
from models.campaign_model import Campaign, CampaignCreate, CampaignUpdate
from services.user_service import UserService

user_service = UserService()


class CampaignService:
    def __init__(self):
        self.client = MongoClient(Config.MONGO_URI)
        self.db = self.client['RoleForge']
        self.campaigns_collection = self.db['Campaigns']

    def get_all_campaigns(self) -> List[Campaign] | None:
        campaigns = list(self.campaigns_collection.find())
        if not campaigns:
            return None

        return get_campaigns_with_users(campaigns)

    def get_campaigns_by_master(self, campaign_master: str) -> List[Campaign] | None:
        campaigns = list(self.campaigns_collection.find({'master': ObjectId(campaign_master)}))
        if not campaigns:
            return []

        return get_campaigns_with_users(campaigns)

    def get_campaign_by_id(self, campaign_id: str) -> Campaign | None:
        campaign = self.campaigns_collection.find_one({'_id': ObjectId(campaign_id)})
        if campaign is None:
            return None

        master = user_service.get_user_by_id(campaign['master'])
        players = user_service.get_users_by_ids(campaign['players'])

        return Campaign(id=str(campaign['_id']), name=campaign['name'], description=campaign['description'],
                        master=master, players=players, character_sheet=campaign['character_sheet'])

    def get_campaigns_by_ids(self, campaign_ids: List[str]) -> List[Campaign] | None:
        campaign_object_ids = list(map(ObjectId, campaign_ids))
        campaigns = list(self.campaigns_collection.find({'_id': {"$in": campaign_object_ids}}))
        if campaigns is None:
            return None
        return get_campaigns_with_users(campaigns)

    def create_campaign(self, campaign: CampaignCreate) -> dict[str, str] | None:
        try:
            new_campaign = campaign.model_dump()

            new_campaign['master'] = ObjectId(new_campaign['master'])
            new_campaign['players'] = [ObjectId(player) for player in new_campaign['players']]

            result = self.campaigns_collection.insert_one(new_campaign)
            return {"detail": "Campanha cadastrada com sucesso!", "id": str(result.inserted_id)}
        except ValidationError as e:
            print(f"Validation Error: {e}")
            return None

    def update_campaign(self, campaign_id: str, campaign: CampaignUpdate) -> dict[str, str] | None:
        update_data = {k: v for k, v in campaign.model_dump().items() if v is not None}

        if 'master' in update_data:
            update_data['master'] = ObjectId(update_data['master'])
        if 'players' in update_data:
            update_data['players'] = [ObjectId(player) for player in update_data['players']]

        updated_campaign = self.campaigns_collection.find_one_and_update(
            {'_id': ObjectId(campaign_id)},
            {'$set': update_data},
            return_document=True
        )

        if updated_campaign is None:
            return None
        return {"detail": "Campanha atualizada com sucesso!", "id": str(updated_campaign['_id'])}

    def delete_campaign(self, campaign_id: str) -> bool:
        result = self.campaigns_collection.delete_one({'_id': ObjectId(campaign_id)})
        return result.deleted_count > 0


def get_campaigns_with_users(campaigns: List[Campaign]):
    user_ids = set()
    for campaign in campaigns:
        user_ids.add(campaign['master'])
        user_ids.update(campaign['players'])

    users = user_service.get_users_by_ids(list(user_ids))
    user_map = {user.id: user for user in users}

    result = []
    for campaign in campaigns:
        master = user_map.get(str(campaign['master']))
        players = [user_map.get(str(player_id)) for player_id in campaign['players']]
        result.append(Campaign(
            id=str(campaign['_id']),
            name=campaign['name'],
            description=campaign['description'],
            master=master,
            players=players,
            character_sheet=campaign['character_sheet']
        ))

    return result
