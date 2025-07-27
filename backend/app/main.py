from fastapi import FastAPI,status,Depends,HTTPException,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.app.auth import router as auth_router
from backend.app.english_test import router as engtest_router
from backend.app.profile import router as profile_router
from fastapi.staticfiles import StaticFiles
import os 

os.makedirs("media/avatars", exist_ok=True)
app = FastAPI()

app.mount("/media", StaticFiles(directory="media"), name="media")


app.include_router(auth_router, prefix="/auth")
app.include_router(engtest_router,prefix="/test")
app.include_router(profile_router,prefix="/profile")


origins = [
    "http://localhost:3000", 
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)