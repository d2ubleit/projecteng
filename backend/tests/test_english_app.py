import uuid
import pytest
from sqlalchemy.orm import Session
from backend.app.models import User, Question, Option, UserAnswer
from backend.app.english_test import (
    generate_diagnostic_test,
    submit_answer,
    evaluate_english_level,
    submit_diagnostic
)


@pytest.fixture
def mock_user(db: Session):
    uid = uuid.uuid4().hex[:8]
    user = User(
        username=f"user_{uid}",
        email=f"user_{uid}@example.com",
        hashed_password="hashed_pass",
        english_level="unknown"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_generate_diagnostic_test(db: Session, mock_user):
    result = generate_diagnostic_test(mock_user.id, db)
    assert "session_id" in result
    assert len(result["questions"]) == 15


def test_submit_answer(db: Session, mock_user):
    payload = generate_diagnostic_test(mock_user.id, db)
    session_id = uuid.UUID(payload["session_id"])
    questions = payload["questions"]

    answers = []
    for q in questions[:5]:
        opt = db.query(Option).filter_by(question_id=q.id).first()
        answers.append({
            "session_id": session_id,
            "question_id": q.id,
            "selected_option_id": opt.id
        })

    result = submit_answer(answers, db)
    assert result["message"] == "Ответы успешно сохранены"


def test_evaluate_english_level_b1_logic(db: Session, mock_user):
    payload = generate_diagnostic_test(mock_user.id, db)
    session_id = uuid.UUID(payload["session_id"])
    questions = payload["questions"]

    user_answers = []
    b1_count = 0

    for q in questions:
        option = db.query(Option).filter_by(question_id=q.id).first()
        is_correct = q.level.value == "B1"
        if is_correct:
            b1_count += 1

        ua = UserAnswer(
            session_id=session_id,
            question_id=q.id,
            selected_option_id=option.id,
            is_correct=is_correct
        )
        db.add(ua)
        user_answers.append(ua)

    db.commit()
    assert b1_count > 0, "❗ В тесте нет вопросов уровня B1 — диагностика невозможна"

    diagnosed_level = evaluate_english_level(user_answers, db)
    assert diagnosed_level == "B1", f"Ожидался B1, получено: {diagnosed_level}"


def test_submit_diagnostic_all_correct_returns_c2(db: Session, mock_user):
    payload = generate_diagnostic_test(mock_user.id, db)
    session_id = uuid.UUID(payload["session_id"])
    questions = payload["questions"]

    for q in questions:
        correct_option = db.query(Option).filter_by(question_id=q.id, is_correct=True).first()
        ua = UserAnswer(
            session_id=session_id,
            question_id=q.id,
            selected_option_id=correct_option.id,
            is_correct=True
        )
        db.add(ua)

    db.commit()
    result = submit_diagnostic(session_id, db)
    assert result["diagnosed_level"] == "C2", f"Ожидался C2, получено: {result['diagnosed_level']}"


def test_submit_diagnostic_all_wrong_returns_a1(db: Session, mock_user):
    payload = generate_diagnostic_test(mock_user.id, db)
    session_id = uuid.UUID(payload["session_id"])
    questions = payload["questions"]

    for q in questions:
        wrong_option = db.query(Option).filter_by(question_id=q.id, is_correct=False).first()
        ua = UserAnswer(
            session_id=session_id,
            question_id=q.id,
            selected_option_id=wrong_option.id,
            is_correct=False
        )
        db.add(ua)

    db.commit()
    result = submit_diagnostic(session_id, db)
    assert result["diagnosed_level"] == "A1", f"Ожидался A1, получено: {result['diagnosed_level']}"
