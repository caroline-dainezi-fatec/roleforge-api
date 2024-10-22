from pydantic import BaseModel
from typing import List


class CharacterSheet(BaseModel):
    fields: List[str]
    attributes: List[str]


class CharacterSheetCreate(BaseModel):
    fields: List[str]
    attributes: List[str]


class CharacterSheetUpdate(BaseModel):
    fields: List[str] = None
    attributes: List[str] = None
