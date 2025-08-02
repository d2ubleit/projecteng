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

    selected_option_id: Optional[UUID] = None   # multiple_choice
    answer_text: Optional[str] = None           # open_text
    match_pairs: Optional[dict[str, str]] = None  # drag_and_drop



class SubmitAnswersRequest(BaseModel):
    answers: List[AnswerPayload]

class SubmitAnswersResponse(BaseModel):
    message: str

class OptionResponse(BaseModel):
    id: UUID
    text: str

    model_config = {
        "from_attributes": True
    }

class DragItemResponse(BaseModel):
    id: UUID
    label: str
    target_key: str

    model_config = {
        "from_attributes": True
    }

class DropTargetResponse(BaseModel):
    id: UUID
    placeholder: str
    target_key: str

    model_config = {
        "from_attributes": True
    }


class QuestionResponse(BaseModel):
    id: UUID
    prompt: str
    level: str
    category: str
    type: str

    options: Optional[List[OptionResponse]] = []           # multiple_choice
    drag_items: Optional[List[DragItemResponse]] = []      # drag_and_drop
    drop_targets: Optional[List[DropTargetResponse]] = []  # drag_and_drop

    #open_text на фронте

    model_config = {
        "from_attributes": True
    }



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





