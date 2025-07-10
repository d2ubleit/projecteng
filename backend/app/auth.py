from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session
from .models import User
from backend.database.database import get_db
from pydantic import BaseModel, model_validator
import redis
import logging
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from backend.database.config import SECRET_KEY
from datetime import datetime, timedelta
from .schemas import UserCreate, UserResponse, Token, UserLogin


#logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url("redis://redis:6379/0")

#jwt token settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 


router = APIRouter()

#support functions
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str,hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_identifier(db:Session, identifier: str) -> Optional[User]:
    return db.query(User).filter(
        (User.username == identifier) | (User.email == identifier)
    ).first()


def create_user(db:Session, user:UserCreate) -> User:
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username = user.username,
        email = user.email,
        hashed_password = hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(db: Session, identifier: str, password: str) -> Optional[User]:
    user = get_user_by_identifier(db,identifier)
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token:str) -> str:
    if redis_client.sismember("token_blacklist", token):
        logger.info(f"Token {token} is blacklisted")
        raise HTTPException(
            status_code = 403,
            detail= "Токен отозван"
        )
    try:
        payload = jwt.decode(token,SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=403,
                detail="" \
                "Не удалось извлечь идентификатор пользователя из токена"
            )
        logger.info(f"Token {token} успешно проверен для пользователя с id {user_id}")
        return user_id
    except JWTError as e:
        logger.warning(f"JWT encode провален: {e}")
        raise HTTPException(
            status_code=403,
            detail="Неверный токен или истек срок его действия"
        )
    

#API endpoints
@router.post("/register",response_model=UserResponse)
def register_user(user:UserCreate,db: Session = Depends(get_db)):
    identifier = user.username or user.email
    db_user = get_user_by_identifier(db, identifier)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем или email уже существует"
        )
    created_user = create_user(db, user)
    return UserResponse(
        id = str(created_user.id),
        username=created_user.username,
        email=created_user.email
    )

@router.post("/token", response_model=Token)
def login_for_access(form_data: UserLogin, db: Session = Depends(get_db)):
    identifier = form_data.username or form_data.email
    user = authenticate_user(db, identifier, form_data.password)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Неверные username/enail/password",
            headers= {"WWW-Authenticate": "Bearer" if form_data.username else "Basic"}
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }

@router.get("/verify-token/{token}")
async def verify_user_token(token:str):
    user_id = verify_token(token)
    return {"user_id":user_id}

@router.post("/logout")
def logout(token: str):
    redis_client.sadd("token_blacklist", token)
    logger.info(f"Token {token} успешно отозван")
    return {"message": "Вы успешно вышли из системы"}
             
        

      








