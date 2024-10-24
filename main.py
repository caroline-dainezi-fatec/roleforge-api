from fastapi import FastAPI
from app.controllers.user_controller import UserController
from app.controllers.campaign_controller import CampaignController
from app.controllers.character_controller import CharacterController

app = FastAPI()

user_controller = UserController()
campaign_controller = CampaignController()
character_controller = CharacterController()

app.include_router(user_controller.router, prefix="/users")
app.include_router(campaign_controller.router, prefix="/campaigns")
app.include_router(character_controller.router, prefix="/characters")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
