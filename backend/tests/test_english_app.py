import uuid
import pytest
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.app.english_test import (
    select_english_level,
    generate_level_progression_test,
    submit_diagnostic,
)
from backend.app.models import (
    User, Question, Option, UserAnswer,
    EnglishTestSession, EnglishLevel
)
from backend.app.english_test_schemas import (
    SelectLevelRequest,
    SubmitAnswersRequest
)

@pytest.fixture
def db() -> Session:
    return SessionLocal()

@pytest.fixture
def test_user(db: Session):
    user = User(
        username=f"user_{uuid.uuid4().hex[:6]}",
        email=f"user_{uuid.uuid4().hex[:6]}@example.com",
        hashed_password="test_password",
        english_level=EnglishLevel.unknown
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def test_select_level(db, test_user):
    """Проверка установки уровня вручную"""
    payload = SelectLevelRequest(level=EnglishLevel.B2)
    response = select_english_level(payload, user=test_user, db=db)
    assert response["level"] == "B2"
    assert test_user.english_level == EnglishLevel.B2

def test_generate_level_test(db, test_user):
    """Генерация прогресс-теста — учитываем лимит 5 вопросов на уровень"""
    test_user.english_level = EnglishLevel.B1
    db.commit()
    result = generate_level_progression_test(test_user.id, db)
    assert result.session_id is not None

    #  Ожидаем максимум 10 вопросов, так как в БД по 5 на каждый уровень
    assert 5 <= len(result.questions) <= 10

    levels_in_test = set(q.level for q in result.questions)
    assert levels_in_test.issubset({"B1", "B2"})


def test_submit_diagnostic_success(db, test_user):
    """Проверка расчета уровня после завершения диагностического теста"""
    session = EnglishTestSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        level=EnglishLevel.unknown,
        score=0,
        completed=False
    )
    db.add(session)
    db.commit()

    # Выбираем 5 вопросов уровня B1 и отвечаем 3 правильно
    questions = db.query(Question).filter_by(level=EnglishLevel.B1).limit(5).all()
    for i, q in enumerate(questions):
        opts = db.query(Option).filter_by(question_id=q.id).all()
        chosen = next((o for o in opts if o.is_correct), opts[0]) if i < 3 else next((o for o in opts if not o.is_correct), opts[0])
        db.add(UserAnswer(
            session_id=session.id,
            question_id=q.id,
            selected_option_id=chosen.id,
            is_correct=(i < 3)
        ))
    db.commit()

    response = submit_diagnostic(session.id, db)
    assert response.diagnosed_level in [lvl.value for lvl in EnglishLevel]
    updated_user = db.query(User).get(test_user.id)
    assert updated_user.english_level.value == response.diagnosed_level
