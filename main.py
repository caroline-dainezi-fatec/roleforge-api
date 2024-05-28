from fastapi import FastAPI
from controllers.user_controller import router as user_router

app = FastAPI()

app.include_router(user_router, prefix="/users")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
