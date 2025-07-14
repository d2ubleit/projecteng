from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from .models import User
from backend.database.database import get_db
from pydantic import BaseModel, model_validator
from .auth import get_current_user
from .auth_schemas import UserResponse
# from .english_test_schemas import 

router = APIRouter()


#ЭНДПОИНТ ВЫЗЫВАЕТСЯ КОГДА ЮЗЕР КЛИКАЕТ НА ЧТО ТО ПО ТИПУ "Я ЗНАЮ СВОЙ УРОВЕНЬ" И ТАМ ВЫБИРАЕТ УРОВЕНЬ АНГЛИЙСКОГО ЯЗЫКА
@router.post("/select-level")
def select_english_level(level:str, user:User =Depends(get_current_user), db: Session = Depends(get_db)):
    user.english_level = level
    db.commit()
    return {"message" : "Уровень английского языка успешно обновлен", "level": level}


