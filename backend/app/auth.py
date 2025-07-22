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
from .auth_schemas import LogoutResponse, TokenVerificationResponse, UserCreate, UserResponse, Token, UserLogin
from fastapi.security import OAuth2PasswordBearer

#logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_client = redis.Redis.from_url("redis://redis:6379/0")

#jwt token settings
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"  #шифрование 
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  

router = APIRouter()


#support functions


def get_current_user(token: str = Depends(oauth2_scheme),db: Session= Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code = 403,
                detail = "Недействительный токен"
            )
        user = db.query(User).get(user_id)
        if not user:
            raise HTTPException(
                status_code=403,
                detail="Пользователь не найден"
            )
        return user 
    except JWTError:
        raise HTTPException(
            status_code=403,
            detail="Неверный токен или истек срок его действия"
        )

        
        


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)  #хэширует пароль пользователя перед сохранением в базу данных


def verify_password(plain_password: str,hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)  # проверяет соответствует ли введённый пароль хэшу в базе (используется при входе)





def create_user(db:Session, user:UserCreate) -> User:  #создаёт нового пользователя в базе данных (может использовать Email/Username для регистраци)
    hashed_password = get_password_hash(user.password)  
    db_user = User(
    username=user.username,
    email=user.email or None,  # email необязательный
    hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


#проверяет логин и пароль пользователя, возвращает объект пользователя при успешной аутентификации
def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    user = db.query(User).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str: #cоздаёт JWT токен для авторизации включая время истечения
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token:str) -> str: #проверяет действительность токена 
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
@router.post("/register",response_model=UserResponse) #регистрация пользователя (username/email + password)
def register_user(user:UserCreate,db: Session = Depends(get_db)):
    db_user = db.query(User).filter_by(username=user.username).first()
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

@router.post("/token", response_model=Token) #логин пользователя (username/email + password) 
def login_for_access(form_data: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Неверные username/password",
            headers= {"WWW-Authenticate": "Bearer" if form_data.username else "Basic"}
        )
    access_token = create_access_token(data={"sub": str(user.id)})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(user.id)
    }


@router.get("/verify-token/{token}", response_model=TokenVerificationResponse)
 #проверка токена пользователя,можно использовать на фронте при каждом запуске или обновлении страницы
async def verify_user_token(token:str):
    user_id = verify_token(token)
    return {"user_id":user_id}


@router.post("/logout", response_model=LogoutResponse)
 #выход пользователя из системы, отзыва токена
def logout(token: str):
    redis_client.sadd("token_blacklist", token)
    logger.info(f"Token {token} успешно отозван")
    return {"message": "Вы успешно вышли из системы"}
             
        

      








