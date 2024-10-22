from fastapi import APIRouter, HTTPException
from typing import List

from app.models.campaign_model import Campaign, CampaignCreate, CampaignUpdate
from app.services.campaign_service import CampaignService
from app.services.user_service import UserService


class CampaignController:
    def __init__(self):
        self.router = APIRouter()
        self.campaign_service = CampaignService()
        self.user_service = UserService()
        self.register_routes()

    def register_routes(self):
        self.router.get("/", response_model=List[Campaign])(self.get_campaigns)
        self.router.get("/master/{campaign_master}", response_model=List[Campaign])(self.get_campaigns_by_master)
        self.router.get("/player/{campaign_player}", response_model=List[Campaign])(self.get_campaigns_by_player)
        self.router.get("/{campaign_id}", response_model=Campaign)(self.get_campaign_by_id)
        self.router.post("/", response_model=dict[str, str])(self.create_campaign)
        self.router.put("/{campaign_id}", response_model=dict[str, str])(self.update_campaign)
        self.router.delete("/{campaign_id}", response_model=dict)(self.delete_campaign)

    def get_campaigns(self):
        campaigns = self.campaign_service.get_all_campaigns()
        if not campaigns:
            raise HTTPException(status_code=404, detail="Nenhuma campanha encontrada.")
        return campaigns

    def get_campaigns_by_master(self, campaign_master: str):
        campaigns = self.campaign_service.get_campaigns_by_master(campaign_master)
        if not campaigns:
            raise HTTPException(status_code=404, detail="Este usuário não possui campanhas.")
        return campaigns

    def get_campaigns_by_player(self, campaign_player: str):
        campaigns = self.campaign_service.get_campaigns_by_player(campaign_player)
        if not campaigns:
            raise HTTPException(status_code=404, detail="Este usuário não participa de nenhuma campanha.")
        return campaigns

    def get_campaign_by_id(self, campaign_id: str):
        campaign = self.campaign_service.get_campaign_by_id(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=404, detail="Campanha não encontrada.")
        return campaign

    def create_campaign(self, campaign: CampaignCreate):
        if self.user_service.get_user_by_id(campaign.master) is None:
            raise HTTPException(status_code=400, detail="O mestre dessa campanha não foi encontrado.")
        if len(self.user_service.get_users_by_ids(campaign.players)) < len(campaign.players):
            raise HTTPException(status_code=400, detail="Um ou mais jogadores dessa campanha não foram encontrados.")
        return self.campaign_service.create_campaign(campaign)

    def update_campaign(self, campaign_id: str, campaign: CampaignUpdate):
        updated_campaign = self.campaign_service.update_campaign(campaign_id, campaign)
        if updated_campaign is None:
            raise HTTPException(status_code=404, detail="Campanha não encontrada.")
        return updated_campaign

    def delete_campaign(self, campaign_id: str):
        if not self.campaign_service.delete_campaign(campaign_id):
            raise HTTPException(status_code=404, detail="Campanha não encontrada.")
        return {"message": "Campanha excluída com sucesso."}
