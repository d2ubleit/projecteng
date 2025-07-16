import uuid 
from sqlalchemy import Column, String,Enum,ForeignKey,Text,Integer,Boolean,JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base,relationship
import enum

Base = declarative_base()

class EnglishLevel(enum.Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
    unknown = "unknown"
    

class User(Base):   
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=True, index=True)  
    email = Column(String, unique=True, nullable=True, index=True)     
    hashed_password = Column(String, nullable=False)
    english_level = Column(Enum(EnglishLevel),default=EnglishLevel.unknown)

class QuestionCategory(enum.Enum):
    grammar = "grammar"
    vocabulary = "vocabulary" #лексика

class QuestionType(enum.Enum):
    multiple_choice = "multiple_choice" #выбор варианта ответа из нескольких
    open_text = "open_text" #вписать текст/слово в поле 
    drag_and_drop = "drag_and_drop" #перетаскивание слов

class LevelUpgradeRequest(Base):
    __tablename__ = "level_upgrade_requests"
    id = Column(UUID(as_uuid=True),primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True),ForeignKey("users.id"),nullable=False)
    target_level = Column(Enum(EnglishLevel), nullable=False) #уровень, на который пользователь хочет повысить свой уровень
    passed = Column(Boolean, default=False)  #статус запроса на повышение уровня 

    user = relationship("User")
    
class EnglishTestSession(Base):
    __tablename__ = "test_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    level = Column(Enum(EnglishLevel), nullable=False)  #уровень теста
    score = Column(Integer,nullable=False)  #результат теста
    completed = Column(Boolean, default=False)  #статус завершения теста

    user = relationship("User")

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt = Column(Text, nullable=False)  #текст вопроса
    level = Column(Enum(EnglishLevel),nullable=False)  #уровень вопроса
    category = Column(Enum(QuestionCategory), nullable=False)  #категория вопроса
    type = Column(Enum(QuestionType), nullable=False)  #тип вопроса
    correct_answer = Column(Text,nullable=True)  #правильный ответ для вопросов с открытым текстом (вписать вариант ответа)


class Option(Base): 
    __tablename__ = "options"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)

    question = relationship("Question", backref="options")

class UserAnswer(Base):
    __tablename__ = "user_answers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("test_sessions.id"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    selected_option_id = Column(UUID(as_uuid=True), ForeignKey("options.id"), nullable=True)  #если вопрос с выбором ответа
    answer_text = Column(Text, nullable=True)
    is_correct = Column(Boolean, nullable=False)  #правильный ли ответ
    feedback = Column(Text, nullable=True)  #обратная связь по ответу
    match_pairs = Column(JSONB, nullable=True)  # ключи drag_item_id -> drop_target_id


    question = relationship("Question")
    session = relationship("EnglishTestSession")

class DragItem(Base):
    __tablename__ = "drag_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    label = Column(String, nullable=False)  #текст перетаскиваемого элемента
    target_key = Column(String, nullable=False)  #ключ для сопоставления элемента в правильнкю позицию 

    question = relationship("Question", backref="drag_items")

class DropTarget(Base):
    __tablename__ = "drop_targets"

    id= Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    placeholder = Column(String, nullable=False)  #текст подсказки 
    target_key = Column(String, nullable=False)  #ключ для сопоставления с DragItem

    question = relationship("Question", backref="drop_targets")


class WordTile(Base):
    __tablename__ = "word_tiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    text = Column(String, nullable=False)  # слово/фраза
    correct_position = Column(Integer, nullable=True)  # если важен порядок

    question = relationship("Question", backref="word_tiles")











