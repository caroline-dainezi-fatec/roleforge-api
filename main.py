from fastapi import FastAPI
from controllers.user_controller import router as user_router
from controllers.campaign_controller import router as campaign_router
from controllers.character_controller import router as character_router

app = FastAPI()

app.include_router(user_router, prefix="/users")
app.include_router(campaign_router, prefix="/campaigns")
app.include_router(character_router, prefix="/characters")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
