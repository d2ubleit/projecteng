import uuid
import pytest
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.app.english_test import (
    select_english_level,
    generate_level_progression_test,
    generate_diagnostic_test,
    generate_upgrade_test,
    submit_diagnostic,
    submit_answer,
    evaluate_upgrade_test
)
from backend.app.models import (
    User, Question, Option, UserAnswer,
    EnglishTestSession, EnglishLevel,
    DragItem, QuestionType,
    LevelUpgradeRequest
)
from backend.app.english_test_schemas import (
    SelectLevelRequest,
    SubmitAnswersRequest
)

# Fixtures
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

# Tests
def test_select_level(db, test_user):
    payload = SelectLevelRequest(level=EnglishLevel.B2)
    response = select_english_level(payload, user=test_user, db=db)
    assert response["level"] == "B2"
    assert test_user.english_level == EnglishLevel.B2

def test_generate_level_test(db, test_user):
    test_user.english_level = EnglishLevel.B1
    db.commit()
    result = generate_level_progression_test(test_user.id, db)
    assert result.session_id
    assert len(result.questions) >= 3  # адаптировано под ограниченную базу
    levels = set(q.level for q in result.questions)
    assert levels.issubset({"B1", "B2"})

def test_generate_diagnostic_test(db, test_user):
    result = generate_diagnostic_test(test_user.id, db)
    assert result.session_id
    assert len(result.questions) >= 6  # адаптировано
    levels = set(q.level for q in result.questions)
    assert levels.issubset({"A1", "A2", "B1", "B2", "C1", "C2"})

def test_generate_upgrade_test(db, test_user):
    test_user.english_level = EnglishLevel.B1
    db.commit()
    result = generate_upgrade_test(test_user.id, db)
    assert result.session_id
    assert len(result.questions) >= 3  # адаптировано
    assert result.target_levels == ["B2"]

    upgrade_request = db.query(LevelUpgradeRequest).filter_by(user_id=test_user.id).first()
    assert upgrade_request is not None
    assert upgrade_request.target_level == EnglishLevel.B2

def test_submit_answer_open_text(db, test_user):
    question = db.query(Question).filter_by(type=QuestionType.open_text).first()
    assert question is not None
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
    question = db.query(Question).filter_by(type=QuestionType.drag_and_drop).first()
    assert question is not None
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
    session = EnglishTestSession(id=uuid.uuid4(), user_id=test_user.id, level=EnglishLevel.unknown, score=0, completed=False)
    db.add(session)
    db.commit()

    # MULTIPLE CHOICE
    mc_questions = db.query(Question).filter_by(type=QuestionType.multiple_choice).limit(2).all()
    for i, q in enumerate(mc_questions):
        opts = db.query(Option).filter_by(question_id=q.id).all()
        chosen = next((o for o in opts if o.is_correct), opts[0]) if i == 0 else next((o for o in opts if not o.is_correct), opts[0])
        db.add(UserAnswer(session_id=session.id, question_id=q.id, selected_option_id=chosen.id, is_correct=(i == 0)))

    # OPEN TEXT
    ot_questions = db.query(Question).filter_by(type=QuestionType.open_text).limit(2).all()
    for i, q in enumerate(ot_questions):
        submitted = q.correct_answer if i == 0 else "wrong"
        db.add(UserAnswer(session_id=session.id, question_id=q.id, answer_text=submitted, is_correct=(submitted.strip().lower() == q.correct_answer.strip().lower())))

    # DRAG AND DROP
    dd_questions = db.query(Question).filter_by(type=QuestionType.drag_and_drop).limit(2).all()
    for i, q in enumerate(dd_questions):
        drag_items = db.query(DragItem).filter_by(question_id=q.id).all()
        correct_map = {item.id.hex: item.target_key for item in drag_items}
        submitted = correct_map if i == 0 else {k: "wrong" for k in correct_map}
        db.add(UserAnswer(session_id=session.id, question_id=q.id, match_pairs=submitted, is_correct=(i == 0)))

    db.commit()
    response = submit_diagnostic(session.id, db)
    assert response.diagnosed_level in [lvl.value for lvl in EnglishLevel]
    updated_user = db.get(User, test_user.id)
    assert updated_user.english_level.value == response.diagnosed_level

def test_evaluate_upgrade_test_success(db, test_user):
    test_user.english_level = EnglishLevel.B1
    db.commit()

    session = EnglishTestSession(id=uuid.uuid4(), user_id=test_user.id, level=EnglishLevel.B2, score=0, completed=False)
    db.add(session)

    upgrade_request = LevelUpgradeRequest(user_id=test_user.id, target_level=EnglishLevel.B2)
    db.add(upgrade_request)
    db.commit()

    questions = db.query(Question).filter_by(level=EnglishLevel.B2.value).limit(3).all()
    for q in questions:
        db.add(UserAnswer(session_id=session.id, question_id=q.id, is_correct=True))
    db.commit()

    response = evaluate_upgrade_test(session.id, db)
    assert response.diagnosed_level == EnglishLevel.B2.value
    updated_user = db.get(User, test_user.id)
    assert updated_user.english_level.value == EnglishLevel.B2.value

def test_evaluate_upgrade_test_failure(db, test_user):
    test_user.english_level = EnglishLevel.B1
    db.commit()

    session = EnglishTestSession(id=uuid.uuid4(), user_id=test_user.id, level=EnglishLevel.B2, score=0, completed=False)
    db.add(session)

    upgrade_request = LevelUpgradeRequest(user_id=test_user.id, target_level=EnglishLevel.B2)
    db.add(upgrade_request)
    db.commit()

    questions = db.query(Question).filter_by(level=EnglishLevel.B2.value).limit(3).all()
    for q in questions:
        db.add(UserAnswer(session_id=session.id, question_id=q.id, is_correct=False))
    db.commit()

    response = evaluate_upgrade_test(session.id, db)
    assert response.diagnosed_level == EnglishLevel.B1.value
    updated_user = db.get(User, test_user.id)
    assert updated_user.english_level.value == EnglishLevel.B1.value
