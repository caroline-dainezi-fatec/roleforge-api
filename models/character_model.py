from pydantic import BaseModel, Field
from typing import Dict, Any
from models.user_model import User
from models.campaign_model import Campaign


class Character(BaseModel):
    id: str
    player: User
    campaign: Campaign
    player_character_sheet: Dict[str, Any] = Field(default_factory=dict)


class CharacterCreate(BaseModel):
    player: str
    campaign: str
    player_character_sheet: Dict[str, Any] = Field(default_factory=dict)


class CharacterUpdate(BaseModel):
    player: str = None
    campaign: str = None
    player_character_sheet: Dict[str, Any] = None
