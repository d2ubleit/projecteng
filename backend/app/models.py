import uuid 
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class User(Base):   
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=True, index=True)  
    email = Column(String, unique=True, nullable=True, index=True)     
    hashed_password = Column(String, nullable=False)



