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


@router.get("/", response_model=List[Character])
def get_characters():
    characters = character_service.get_all_characters()
    if not characters:
        raise HTTPException(status_code=404, detail="Nenhum personagem encontrado.")
    return characters


@router.get("/{character_id}", response_model=Character)
def get_character_by_id(character_id: str):
    character = character_service.get_character_by_id(character_id)
    if character is None:
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")
    return character


@router.get("/player/{character_player}", response_model=List[Character])
def get_characters_by_player(character_player: str):
    characters = character_service.get_characters_by_player(character_player)
    if characters is None:
        raise HTTPException(status_code=404, detail="Este usuário não possui personagens.")
    return characters


@router.post("/", response_model=dict[str, str])
def create_character(character: CharacterCreate):
    if user_service.get_user_by_id(character.player) is None:
        raise HTTPException(status_code=400, detail="O jogador desse personagem não foi encontrado.")
    if campaign_service.get_campaign_by_id(character.campaign) is None:
        raise HTTPException(status_code=400, detail="A campanha desse personagem não foi encontrada.")
    return character_service.create_character(character)


@router.put("/{character_id}", response_model=dict[str, str])
def update_character(character_id: str, character: CharacterUpdate):
    updated_character = character_service.update_character(character_id, character)
    if updated_character is None:
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")
    return updated_character


@router.delete("/{character_id}", response_model=dict)
def delete_character(character_id: str):
    if not character_service.delete_character(character_id):
        raise HTTPException(status_code=404, detail="Personagem não encontrado.")
    return {"message": "Personagem excluído com sucesso."}
