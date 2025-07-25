from fastapi import APIRouter, Depends
from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session
from .models import User
from backend.database.database import get_db
from .auth import get_current_user
from backend.app.models import Question,EnglishTestSession,UserAnswer,Option,User,EnglishLevel
from sqlalchemy.sql import func
from uuid import UUID, uuid4
from collections import defaultdict

from .english_test_schemas import GenerateTestResponse, QuestionResponse,SubmitAnswersRequest,SelectLevelRequest, SubmitAnswersResponse,SubmitDiagnosticResponse,SelectLevelResponse

router = APIRouter()


#ЭНДПОИНТ ВЫЗЫВАЕТСЯ КОГДА ЮЗЕР КЛИКАЕТ НА ЧТО ТО ПО ТИПУ "Я ЗНАЮ СВОЙ УРОВЕНЬ" И ТАМ ВЫБИРАЕТ УРОВЕНЬ АНГЛИЙСКОГО ЯЗЫКА
@router.post("/select-level", response_model=SelectLevelResponse)
def select_english_level(payload: SelectLevelRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user.english_level = payload.level
    db.commit()
    return {"message": "Уровень английского языка успешно обновлен", "level": user.english_level.value}


def generate_diagnostic_test(user_id: UUID, db: Session) -> GenerateTestResponse:
    """
    Функция для генерации теста, если пользователь не знает свой уровень англ

    """
    session = EnglishTestSession(
        id=uuid4(),
        user_id=user_id,
        level="unknown",
        score=0,
        completed=False
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    level_order = ["A1", "A2", "B1", "B2", "C1", "C2"]
    questions = []
    for lvl in level_order:
        q = (
            db.query(Question)
            .filter_by(level=lvl)
            .order_by(func.random())
            .limit(5)  
            .all()
        )
        questions.extend(q)

    questions_serialized = []
    for q in questions:
        options = db.query(Option).filter_by(question_id=q.id).all()
        setattr(q, "options", options)
        questions_serialized.append(QuestionResponse.from_orm(q))

    return GenerateTestResponse(
        session_id=str(session.id),
        questions=questions_serialized
    )

#Функциия сохранения ответов пользователя на вопросы теста
def submit_answer(answers_data: list[dict], db: Session) -> SubmitAnswersResponse:
    """
    answers_data = [
        {
            "session_id": UUID,
            "question_id": UUID,
            "selected_option_id": UUID
        }
    ]
    """

    for entry in answers_data:
        selected_option = db.query(Option).get(entry["selected_option_id"])
        is_correct = selected_option.is_correct if selected_option else False

        user_answer = UserAnswer(
            session_id = entry["session_id"],
            question_id = entry["question_id"],
            selected_option_id = entry["selected_option_id"],
            is_correct = is_correct,
        )

        db.add(user_answer)

    db.commit()
    return SubmitAnswersResponse(message="Ответы успешно сохранены")



def evaluate_english_level(user_answers: list[UserAnswer], db: Session) -> str:
    """
    Примитивный алгоритм оценивания уровня английского 
    """
    level_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    level_order = ["A1", "A2", "B1", "B2", "C1", "C2"]

    for answer in user_answers:
        question = db.query(Question).get(answer.question_id)
        if not question or question.level.value not in level_order:
            continue
        lvl = question.level.value
        level_stats[lvl]["total"] += 1
        if answer.is_correct:
            level_stats[lvl]["correct"] += 1

    if all(stats["total"] == 0 for stats in level_stats.values()):
        return "A1"

    best_level = "A1"
    for lvl in level_order:
        stats = level_stats[lvl]
        if stats["total"] == 0:
            continue

        accuracy = stats["correct"] / stats["total"]
        if accuracy >= 0.6:
            best_level = lvl
        else:
            break

    return best_level



def submit_diagnostic(session_id: UUID, db:Session) -> SubmitDiagnosticResponse:
    """
    Функция для завершения диагностического теста и определения уровня английского пользователя
    """
    answers = db.query(UserAnswer).filter(UserAnswer.session_id == session_id).all()
    if not answers:
        raise HTTPException(
            status_code=400,
            detail="Нет ответов для данной сессии"
        )
    diagnosed_level = evaluate_english_level(answers, db)
    
    # Обновляем пользователя
    session = db.query(EnglishTestSession).get(session_id)
    session.score = sum(1 for ans in answers if ans.is_correct)
    session.completed = True

    user = db.query(User).get(session.user_id)
    user.english_level = diagnosed_level

    db.commit()

    return SubmitDiagnosticResponse(diagnosed_level=diagnosed_level)



def get_next_level(current: EnglishLevel) -> EnglishLevel: 
    """
    Функция для получения следующего уровня английского языка на основе текущего уровня
    """
    level_order = [
        "A1", "A2", "B1", "B2", "C1", "C2"
    ]
    try:
        idx = level_order.index(current.value)
        return EnglishLevel(level_order[min(idx+1,len(level_order)-1)]) 
    except ValueError:
        return EnglishLevel.A1


def generate_level_progression_test(user_id: UUID, db: Session) -> GenerateTestResponse:
    """
    Генерация теста на основе текущего уровня пользователя
    Включает вопросы его уровня и следующего
    """
    user = db.query(User).get(user_id)
    if not user or user.english_level == EnglishLevel.unknown:
        raise HTTPException(
            status_code=400,
            detail="Пользователь не имеет определенного уровня английского языка"
        )

    current_level = user.english_level
    next_level = get_next_level(current_level)
    target_levels = [current_level.value, next_level.value]

    session = EnglishTestSession(
        id=uuid4(),
        user_id=user_id,
        level=current_level,
        score=0,
        completed=False
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    questions = []
    for lvl in target_levels:
        q = (
            db.query(Question)
            .filter_by(level=lvl)
            .order_by(func.random())
            .limit(8 if lvl == target_levels[0] else 7)  
            .all()
        )
        questions.extend(q)

    questions_serialized = []
    for q in questions:
        options = db.query(Option).filter_by(question_id=q.id).all()
        setattr(q, "options", options)
        questions_serialized.append(QuestionResponse.model_validate(q))

    return GenerateTestResponse(
        session_id=str(session.id),
        questions=questions_serialized
    )




@router.post("/generate-diagnostic-test",response_model=GenerateTestResponse)
def diagnostic_test(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Генерация диагностического теста
    """
    result = generate_diagnostic_test(user.id, db)
    return result


@router.post("/submit-diagnostic/{session_id}",response_model=SubmitDiagnosticResponse)
def submit_diagnostic_result(session_id: UUID, db: Session = Depends(get_db)):
    """
    Завершение диагностики и определение уровня
    """
    result = submit_diagnostic(session_id, db)
    return result


@router.post("/generate-level-test",response_model=GenerateTestResponse)
def level_progress_test(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Генерация теста по текущему уровню
    """
    result = generate_level_progression_test(user.id, db)
    return result


@router.post("/submit-answers",response_model=SubmitAnswersResponse)
def submit_answers(payload: SubmitAnswersRequest, db: Session = Depends(get_db)):
    """
    Принимает список ответов и сохраняет их
    """
    return submit_answer(payload.answers, db)


