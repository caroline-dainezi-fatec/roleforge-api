from fastapi import APIRouter, HTTPException
from typing import List
from models.campaign_model import Campaign, CampaignCreate, CampaignUpdate
from services.campaign_service import CampaignService
from services.user_service import UserService

router = APIRouter()
campaign_service = CampaignService()
user_service = UserService()


@router.get("/", response_model=List[Campaign])
def get_campaigns():
    return campaign_service.get_all_campaigns()


@router.get("/{campaign_id}", response_model=Campaign)
def get_campaign_by_id(campaign_id: str):
    campaign = campaign_service.get_campaign_by_id(campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")
    return campaign


@router.get("/master/{campaign_master}", response_model=List[Campaign])
def get_campaigns_by_master(campaign_master: str):
    campaigns = campaign_service.get_campaigns_by_master(campaign_master)
    if campaigns is None:
        raise HTTPException(status_code=404, detail="Este usuário não possui campanhas.")
    return campaigns


@router.post("/", response_model=dict[str, str])
def create_campaign(campaign: CampaignCreate):
    if user_service.get_user_by_id(campaign.master) is None:
        raise HTTPException(status_code=400, detail="O mestre dessa campanha não foi encontrado.")
    if len(user_service.get_users_by_ids(campaign.players)) < len(campaign.players):
        raise HTTPException(status_code=400, detail="Um ou mais jogadores dessa campanha não foram encontrados.")
    return campaign_service.create_campaign(campaign)


@router.put("/{campaign_id}", response_model=dict[str, str])
def update_campaign(campaign_id: str, campaign: CampaignUpdate):
    updated_campaign = campaign_service.update_campaign(campaign_id, campaign)
    if updated_campaign is None:
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")
    return updated_campaign


@router.delete("/{campaign_id}", response_model=dict)
def delete_campaign(campaign_id: str):
    if not campaign_service.delete_campaign(campaign_id):
        raise HTTPException(status_code=404, detail="Campanha não encontrada.")
    return {"message": "Campanha excluída com sucesso."}
