from pymongo import MongoClient
from bson import ObjectId
from typing import List, Mapping, Any
from pydantic import ValidationError
from config import Config

from app.models.character_model import Character, CharacterCreate, CharacterUpdate
from app.services.user_service import UserService
from app.services.campaign_service import CampaignService


class CharacterService:
    def __init__(self):
        self.client = None
        self.db = None
        self.characters_collection = None
        self.campaign_service = CampaignService()
        self.user_service = UserService()

    def get_db(self):
        if self.characters_collection is None:
            self.client = MongoClient(Config.MONGO_URI)
            self.db = self.client['RoleForge']
            self.characters_collection = self.db['Characters']
        return self.characters_collection

    def get_all_characters(self) -> list[Character] | None:
        characters_collection = self.get_db()
        characters = list(characters_collection.find())

        if not characters:
            return []
        return self.get_characters_with_players_and_campaigns(characters)

    def get_characters_by_player(self, player_id: str) -> List[Character] | None:
        characters_collection = self.get_db()
        characters = list(characters_collection.find({'player': ObjectId(player_id)}))

        if not characters:
            return []
        return self.get_characters_with_players_and_campaigns(characters)

    def get_character_by_id(self, character_id: str) -> Character | None:
        characters_collection = self.get_db()
        character = characters_collection.find_one({'_id': ObjectId(character_id)})
        if character is None:
            return None

        player = self.user_service.get_user_by_id(character['player'])
        campaign = self.campaign_service.get_campaign_by_id(character['campaign'])

        return Character(id=str(character['_id']), player=player, campaign=campaign,
                         player_character_sheet=character['player_character_sheet'])

    def create_character(self, character: CharacterCreate) -> dict[str, str] | None:
        characters_collection = self.get_db()

        try:
            new_character = character.model_dump()

            new_character['player'] = ObjectId(new_character['player'])
            new_character['campaign'] = ObjectId(new_character['campaign'])

            result = characters_collection.insert_one(new_character)
            return {"detail": "Personagem cadastrado com sucesso!", "id": str(result.inserted_id)}
        except ValidationError as e:
            print(f"Validation Error: {e}")
            raise

    def update_character(self, character_id: str, character: CharacterUpdate) -> dict[str, str] | None:
        characters_collection = self.get_db()

        update_data = {k: v for k, v in character.model_dump().items() if v is not None}

        if 'player' in update_data:
            update_data['player'] = ObjectId(update_data['player'])
        if 'campaign' in update_data:
            update_data['campaign'] = ObjectId(update_data['campaign'])

        updated_character = characters_collection.find_one_and_update(
            {'_id': ObjectId(character_id)},
            {'$set': update_data},
            return_document=True
        )

        if updated_character is None:
            return None
        return {"detail": "Personagem atualizado com sucesso!", "id": str(updated_character['_id'])}

    def delete_character(self, character_id: str) -> bool:
        characters_collection = self.get_db()

        result = characters_collection.delete_one({'_id': ObjectId(character_id)})
        return result.deleted_count > 0

    def get_characters_with_players_and_campaigns(self, characters: list[Mapping[str, Any]]):
        user_ids = set()
        campaign_ids = set()
        for character in characters:
            user_ids.add(character['player'])
            campaign_ids.add(character['campaign'])

        users = self.user_service.get_users_by_ids(list(user_ids))
        user_map = {user.id: user for user in users}

        campaigns = self.campaign_service.get_campaigns_by_ids(list(campaign_ids))
        campaign_map = {campaign.id: campaign for campaign in campaigns}

        result = []
        for character in characters:
            player = user_map.get(str(character['player']))
            campaign = campaign_map.get(str(character['campaign']))

            result.append(Character(
                id=str(character['_id']),
                player=player,
                campaign=campaign,
                player_character_sheet=character['player_character_sheet']
            ))

        return result
