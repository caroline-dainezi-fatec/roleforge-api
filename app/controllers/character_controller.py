from fastapi import APIRouter, HTTPException
from typing import List

from app.models.character_model import Character, CharacterCreate, CharacterUpdate
from app.services.character_service import CharacterService
from app.services.campaign_service import CampaignService
from app.services.user_service import UserService

router = APIRouter()
character_service = CharacterService()
campaign_service = CampaignService()
user_service = UserService()


class CharacterController:
    def __init__(self):
        self.router = APIRouter()
        self.character_service = CharacterService()
        self.campaign_service = CampaignService()
        self.user_service = UserService()
        self.register_routes()

    def register_routes(self):
        self.router.get("/", response_model=List[Character])(self.get_characters)
        self.router.get("/{character_id}", response_model=Character)(self.get_character_by_id)
        self.router.get("/player/{character_player}", response_model=List[Character])(self.get_characters_by_player)
        self.router.post("/", response_model=dict[str, str])(self.create_character)
        self.router.put("/{character_id}", response_model=dict[str, str])(self.update_character)
        self.router.delete("/{character_id}", response_model=dict)(self.delete_character)

    def get_characters(self):
        characters = self.character_service.get_all_characters()
        if not characters:
            raise HTTPException(status_code=404, detail="Nenhum personagem encontrado.")
        return characters

    def get_character_by_id(self, character_id: str):
        character = self.character_service.get_character_by_id(character_id)
        if character is None:
            raise HTTPException(status_code=404, detail="Personagem não encontrado.")
        return character

    def get_characters_by_player(self, character_player: str):
        characters = self.character_service.get_characters_by_player(character_player)
        if not characters:
            raise HTTPException(status_code=404, detail="Este usuário não possui personagens.")
        return characters

    def create_character(self, character: CharacterCreate):
        if self.user_service.get_user_by_id(character.player) is None:
            raise HTTPException(status_code=400, detail="O jogador desse personagem não foi encontrado.")
        if self.campaign_service.get_campaign_by_id(character.campaign) is None:
            raise HTTPException(status_code=400, detail="A campanha desse personagem não foi encontrada.")
        return self.character_service.create_character(character)

    def update_character(self, character_id: str, character: CharacterUpdate):
        updated_character = self.character_service.update_character(character_id, character)
        if updated_character is None:
            raise HTTPException(status_code=404, detail="Personagem não encontrado.")
        return updated_character

    def delete_character(self, character_id: str):
        if not self.character_service.delete_character(character_id):
            raise HTTPException(status_code=404, detail="Personagem não encontrado.")
        return {"message": "Personagem excluído com sucesso."}
