from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Optional
from uuid import UUID
from fastapi.exceptions import HTTPException

from backend.database.database import get_db
from backend.app.auth import get_current_user
from backend.app.models import EnglishLevel, User, EnglishTestSession, UserAnswer, Question, Option
from backend.app.english_test_schemas import (
    TestHistoryResponse,
    TestHistoryQuestion,
    TestSessionHistory,
    EnglishLevelEnum
)
from backend.app.auth_schemas import UpdateEmailRequest, UserProfileResponse


router = APIRouter()



# получение данных профиля
@router.get("/me", response_model=UserProfileResponse)
def get_profile_info(user: User = Depends(get_current_user)) -> UserProfileResponse:
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "english_level": user.english_level.value
    }




#  Получение истории тестов
@router.get("/history", response_model=TestHistoryResponse)
def get_profile_test_history(user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> TestHistoryResponse:
    """
    Возвращает последние 10 завершённых тестов пользователя — с деталями по каждому вопросу
    """
    sessions = (
        db.query(EnglishTestSession)
        .filter_by(user_id = user.id, completed = True)
        .order_by(EnglishTestSession.id.desc())
        .limit(10)
        .all()
    )

    history = []


    for session in sessions:
        answers = (
            db.query(UserAnswer)
            .filter_by(session_id = session.id)
            .all()
        )

        session_data = {
            "session_id": str(session.id),
            "level": session.level.value,
            "score": session.score,
            "completed": session.completed,
            "questions": []
        }

        for ans in answers:
            question = db.query(Question).get(ans.question_id)
            selected_option = db.query(Option).get(ans.selected_option_id)
            correct_option = (
                db.query(Option)
                .filter_by(question_id=ans.question_id, is_correct=True)
                .first()
            )

        session_data["questions"].append({
                "question_text": question.prompt,
                "user_answer": selected_option.text if selected_option else ans.answer_text,
                "correct_answer": correct_option.text if correct_option else None,
                "is_correct": ans.is_correct
            })

        history.append(session_data)

    return {"history": history}


@router.post("/update-email") 
def update_email(
    payload: UpdateEmailRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    пользователь добвляет email  (опционально) 
    Доделать логику с подтверждением!
    """
    existing = db.query(User).filter_by(email=payload.email).first()
    if existing and existing.id != user.id:
        raise HTTPException(status_code=400, detail="Email уже используется другим пользователем")

    previous_email = user.email
    user.email = payload.email
    db.commit()
    
    action = "обновлён" if previous_email else "добавлен"
    return {"message": f"Email успешно {action}", "email": user.email}