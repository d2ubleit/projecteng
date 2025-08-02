import uuid
import pytest
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.app.english_test import (
    select_english_level,
    generate_level_progression_test,
    generate_diagnostic_test,
    submit_diagnostic,
    submit_answer
)
from backend.app.models import (
    User, Question, Option, UserAnswer,
    EnglishTestSession, EnglishLevel,
    DragItem, DropTarget, QuestionType
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
    """Генерация прогресс-теста"""
    test_user.english_level = EnglishLevel.B1
    db.commit()
    result = generate_level_progression_test(test_user.id, db)
    assert result.session_id is not None
    assert 5 <= len(result.questions) <= 15
    levels_in_test = set(q.level for q in result.questions)
    assert levels_in_test.issubset({"B1", "B2"})

def test_generate_diagnostic_test(db, test_user):
    """Генерация диагностического теста"""
    result = generate_diagnostic_test(test_user.id, db)
    assert result.session_id is not None
    assert len(result.questions) >= 30
    levels_in_test = set(q.level for q in result.questions)
    assert levels_in_test.issubset({"A1", "A2", "B1", "B2", "C1", "C2"})

def test_submit_answer_open_text(db, test_user):
    """Сохранение ответа open_text"""
    question = db.query(Question).filter_by(type=QuestionType.open_text).first()
    session = EnglishTestSession(id=uuid.uuid4(), user_id=test_user.id, level="unknown", score=0, completed=False)
    db.add(session)
    db.commit()

    payload = SubmitAnswersRequest(answers=[
        {
            "session_id": session.id,
            "question_id": question.id,
            "answer_text": question.correct_answer
        }
    ])
    response = submit_answer(payload.answers, db)
    assert response.message == "Ответы успешно сохранены"

def test_submit_answer_drag_and_drop(db, test_user):
    """Сохранение ответа drag_and_drop"""
    question = db.query(Question).filter_by(type=QuestionType.drag_and_drop).first()
    drag_items = db.query(DragItem).filter_by(question_id=question.id).all()
    correct_map = {item.id.hex: item.target_key for item in drag_items}

    session = EnglishTestSession(id=uuid.uuid4(), user_id=test_user.id, level="unknown", score=0, completed=False)
    db.add(session)
    db.commit()

    payload = SubmitAnswersRequest(answers=[
        {
            "session_id": session.id,
            "question_id": question.id,
            "match_pairs": correct_map
        }
    ])
    response = submit_answer(payload.answers, db)
    assert response.message == "Ответы успешно сохранены"

def test_submit_diagnostic_all_types(db, test_user):
    """Диагностика с вопросами всех типов"""
    session = EnglishTestSession(
        id=uuid.uuid4(),
        user_id=test_user.id,
        level=EnglishLevel.unknown,
        score=0,
        completed=False
    )
    db.add(session)
    db.commit()

    # MULTIPLE CHOICE
    mc_questions = db.query(Question).filter_by(type=QuestionType.multiple_choice).limit(2).all()
    for i, q in enumerate(mc_questions):
        opts = db.query(Option).filter_by(question_id=q.id).all()
        chosen = next((o for o in opts if o.is_correct), opts[0]) if i == 0 else next((o for o in opts if not o.is_correct), opts[0])
        db.add(UserAnswer(
            session_id=session.id,
            question_id=q.id,
            selected_option_id=chosen.id,
            is_correct=(i == 0)
        ))

    # OPEN TEXT
    ot_questions = db.query(Question).filter_by(type=QuestionType.open_text).limit(2).all()
    for i, q in enumerate(ot_questions):
        submitted = q.correct_answer if i == 0 else "wrong"
        db.add(UserAnswer(
            session_id=session.id,
            question_id=q.id,
            answer_text=submitted,
            is_correct=(submitted.strip().lower() == q.correct_answer.strip().lower())
        ))

    # DRAG AND DROP
    dd_questions = db.query(Question).filter_by(type=QuestionType.drag_and_drop).limit(2).all()
    for i, q in enumerate(dd_questions):
        drag_items = db.query(DragItem).filter_by(question_id=q.id).all()
        correct_map = {item.id.hex: item.target_key for item in drag_items}
        submitted = correct_map if i == 0 else {k: "wrong" for k in correct_map}
        db.add(UserAnswer(
            session_id=session.id,
            question_id=q.id,
            match_pairs=submitted,
            is_correct=(i == 0)
        ))

    db.commit()

    response = submit_diagnostic(session.id, db)
    assert response.diagnosed_level in [lvl.value for lvl in EnglishLevel]
    updated_user = db.query(User).get(test_user.id)
    assert updated_user.english_level.value == response.diagnosed_level
