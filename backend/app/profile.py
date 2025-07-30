from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from typing import Dict, Optional
from uuid import UUID
from fastapi.exceptions import HTTPException
from PIL import Image
import io

from backend.database.database import get_db
from backend.app.auth import get_current_user
from backend.app.models import EnglishLevel, User, EnglishTestSession, UserAnswer, Question, Option
from backend.app.english_test_schemas import (
    TestHistoryResponse,
    TestHistoryQuestion,
    TestSessionHistory,
    EnglishLevelEnum
)
from backend.app.auth_schemas import UpdateEmailRequest, UserProfileResponse, VerifyEmailRequest
from backend.utils.email_verification import send_verification_code,generate_verification_code
from backend.utils.email import send_email

router = APIRouter()

ALLOWED_TYPES = ["image/png", "image/jpeg", "image/jpg"]
MAX_DIMENSION = 400




# получение данных профиля
@router.get("/me", response_model=UserProfileResponse)
def get_profile_info(user: User = Depends(get_current_user)) -> UserProfileResponse:
    return {
        "id": str(user.id),
        "username": user.username,
        "email": user.email,
        "english_level": user.english_level.value,
        "avatar_url": user.avatar_url
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
    existing = db.query(User).filter_by(email=payload.email).first()
    if existing and existing.id != user.id:
        raise HTTPException(status_code=400, detail="Email уже используется другим пользователем")

    user.email = payload.email
    user.email_verified = False
    user.email_verification_code = generate_verification_code()
    db.commit()

    send_verification_code(email=payload.email, code=user.email_verification_code)

    return {"message": "Код подтверждения отправлен", "email": user.email}


@router.post("/verify-email")
def verify_email(
    payload: VerifyEmailRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.email_verified:
        return {"message": "Email уже подтверждён"}

    if payload.code != user.email_verification_code:
        raise HTTPException(status_code=400, detail="Неверный код подтверждения")

    user.email_verified = True
    user.email_verification_code = None
    db.commit()

    return {"message": "Email успешно подтверждён"}



@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    
    #проверка типа 
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Допустимы только PNG и JPEG"
        )
    
    contents = await file.read()
    
    #проверка размеров
    try:
        image = Image.open(io.BytesIO(contents))
        if image.width > MAX_DIMENSION or image.height > MAX_DIMENSION:
            raise HTTPException(
                status_code=400,
                detail="Изображение не должно превышать 400x400 пикселей"
            )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Файл не является корректным изображением"
        )
    
    filename = f"{user.id}_{file.filename}"
    filepath = f"media/avatars/{filename}"

    with open(filepath, "wb") as f:
        f.write(contents)

    user.avatar_url = f"/media/avatars/{filename}"
    db.commit()

    return {"avatar_url": user.avatar_url}