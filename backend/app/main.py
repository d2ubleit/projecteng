from fastapi import FastAPI,status,Depends,HTTPException,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.app.auth import router as auth_router


app = FastAPI()


app.include_router(auth_router, prefix="/auth")



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