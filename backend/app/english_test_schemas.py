from pydantic import BaseModel, Field
from uuid import UUID
from typing import List, Optional
from enum import Enum


class EnglishLevelEnum(str, Enum):
    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"
    unknown = "unknown"


class SelectLevelRequest(BaseModel):
    level: EnglishLevelEnum


class AnswerPayload(BaseModel):
    session_id: UUID
    question_id: UUID
    selected_option_id: Optional[UUID]  # для текстовых вопросов может быть None


class SubmitAnswersRequest(BaseModel):
    answers: List[AnswerPayload]

class SubmitAnswersResponse(BaseModel):
    message: str



class QuestionResponse(BaseModel):
    id: UUID
    prompt: str
    level: EnglishLevelEnum
    category: str
    type: str


class GenerateTestResponse(BaseModel):
    session_id: str
    target_levels: Optional[List[str]] = None
    questions: List[QuestionResponse]


class SubmitDiagnosticResponse(BaseModel):
    diagnosed_level: EnglishLevelEnum

class TestHistoryQuestion(BaseModel):
    question_text: str
    user_answer: Optional[str]
    correct_answer: Optional[str]
    is_correct: bool

class TestSessionHistory(BaseModel):
    session_id: str
    level: EnglishLevelEnum
    score: int
    completed: bool
    questions: List[TestHistoryQuestion]

class TestHistoryResponse(BaseModel):
    history: List[TestSessionHistory]


class SelectLevelResponse(BaseModel):
    message: str
    level: EnglishLevelEnum


