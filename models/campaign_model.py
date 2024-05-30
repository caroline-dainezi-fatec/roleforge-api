from pydantic import BaseModel
from typing import List
from models.character_sheet_model import CharacterSheet
from models.user_model import User


class Campaign(BaseModel):
    id: str
    name: str
    master: User
    players: List[User]
    character_sheet: CharacterSheet


class CampaignCreate(BaseModel):
    name: str
    master: str
    players: List[str]
    character_sheet: CharacterSheet


class CampaignUpdate(BaseModel):
    name: str = None
    master: str = None
    players: List[str] = None
    character_sheet: CharacterSheet = None
