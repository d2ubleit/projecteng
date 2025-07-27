from pydantic import BaseModel,EmailStr,model_validator,constr,Field
from typing import Optional,Annotated
import re
from uuid import UUID
from backend.app.english_test_schemas import EnglishLevelEnum

USERNAME_REGEX = r"^[a-zA-Z0-9_.-]+$"


class UserCreate(BaseModel):
    username: Annotated[str, constr(min_length=3, max_length=32)]
    email: Optional[EmailStr] = None
    password: Annotated[str, constr(min_length=5, max_length=128)]
    password_repeat: Annotated[str, constr(min_length=5, max_length=128)]

    @model_validator(mode="after")
    def validate_fields(self):
        if not re.fullmatch(USERNAME_REGEX, self.username):
            raise ValueError("Имя пользователя содержит недопустимые символы")
        if self.password != self.password_repeat:
            raise ValueError("Пароли не совпадают")
        return self


    
class UserResponse(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None 
    avatar_url: Optional[str] 

    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str


class UserLogin(BaseModel):
    username: str
    password: str


class UserSchema(BaseModel): #для получения инфы о пользователе к примеру /me
    id:UUID
    username: Optional[str]
    email: Optional[str]
    english_level: str

    model_config = {"from_attributes": True}
    

class UserProfileResponse(BaseModel):
    id: str
    username: str
    email: Optional[str]
    english_level: EnglishLevelEnum
    avatar_url: str



class UpdateEmailRequest(BaseModel):
    email: EmailStr

class TokenVerificationResponse(BaseModel):
    user_id: str


class LogoutResponse(BaseModel):
    message: str
