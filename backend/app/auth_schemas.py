from pydantic import BaseModel,EmailStr,model_validator,constr,Field
from typing import Optional,Annotated
import re
from uuid import UUID


USERNAME_REGEX = r"^[a-zA-Z0-9_.-]+$"


class UserCreate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Annotated[str, constr(min_length=5, max_length=128)]
    password_repeat: Annotated[str, constr(min_length=5, max_length=128)]

    @model_validator(mode="after")
    def check_username_or_email(self):
        if not self.username and not self.email:
            raise ValueError("Необходимо указать либо email, либо имя пользователя")
        if self.username and not re.fullmatch(USERNAME_REGEX, self.username):
            raise ValueError("Имя пользователя содержит недопустимые символы")
        if self.password != self.password_repeat:
            raise ValueError("Пароли не совпадают")
        return self

    
class UserResponse(BaseModel):
    id: str
    username: Optional[str] = None
    email: Optional[str] = None 

    model_config = {
        "from_attributes": True
    }


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: str


class UserLogin(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: str

class UserSchema(BaseModel): #для получения инфы о пользователе к примеру /me
    id:UUID
    username: Optional[str]
    email: Optional[str]
    english_level: str

    model_config = {"from_attributes": True}
    

