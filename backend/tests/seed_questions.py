import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import uuid
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.app.models import Question, Option, EnglishLevel, QuestionType, QuestionCategory

# 👇 Массив вопросов + правильный ответ и варианты
QUESTIONS = [
    {
        "prompt": "Translate the word 'book'.",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Book", True), ("Library", False), ("Paper", False)]
    },
    {
        "prompt": "Complete: 'He ___ a car.'",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("has", True), ("have", False), ("had", False)]
    },
    {
        "prompt": "Choose: 'I ___ happy.'",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("am", True), ("is", False), ("are", False)]
    },
    {
        "prompt": "She is interested ___ music.",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("in", True), ("on", False), ("at", False)]
    },
    {
        "prompt": "'They ___ tennis every week.'",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("play", True), ("plays", False), ("playing", False)]
    },
    {
        "prompt": "Synonym of 'big'?",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("large", True), ("tiny", False), ("weak", False)]
    },
    {
        "prompt": "'Difficult' means...",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("hard", True), ("easy", False), ("light", False)]
    },
    {
        "prompt": "Complete: 'I have been working ___ morning.'",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("since", True), ("from", False), ("by", False)]
    },
    {
        "prompt": "'good ___ math'",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("at", True), ("in", False), ("to", False)]
    },
    {
        "prompt": "No sooner ___ he arrived.",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("had", True), ("has", False), ("have", False)]
    },
    {
        "prompt": "Meaning of 'get over'?",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("recover", True), ("give up", False), ("fall apart", False)]
    },
    {
        "prompt": "Passive: 'The cake ___ baked.'",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("was", True), ("is", False), ("has", False)]
    },
    {
        "prompt": "'Were I you...' means?",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("If I were you", True), ("If I was you", False), ("If I'm you", False)]
    },
    {
        "prompt": "Meaning of 'drop the ball'?",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("fail", True), ("run", False), ("improve", False)]
    },
    {
        "prompt": "Meaning of 'by the skin of your teeth'?",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("barely succeed", True), ("lose badly", False), ("cheat", False)]
    }
]

def seed_questions():
    db: Session = SessionLocal()
    for q in QUESTIONS:
        question = Question(
            prompt=q["prompt"],
            level=q["level"],
            category=q["category"],
            type=q["type"]
        )
        db.add(question)
        db.commit()
        db.refresh(question)

        for text, correct in q["options"]:
            db.add(Option(
                question_id=question.id,
                text=text,
                is_correct=correct
            ))
        db.commit()
    print("✅ Вопросы и варианты загружены")

if __name__ == "__main__":
    seed_questions()
