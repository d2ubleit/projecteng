from fastapi import FastAPI,status,Depends,HTTPException,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.app.auth import router as auth_router


app = FastAPI()


app.include_router(auth_router, prefix="/auth")

