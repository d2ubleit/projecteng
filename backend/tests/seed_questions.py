import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import uuid
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.app.models import Question, Option, EnglishLevel, QuestionType, QuestionCategory

QUESTIONS = [
    # A1 — 5 вопросов
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
        "prompt": "This is a ___.",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("pen", True), ("walk", False), ("go", False)]
    },
    {
        "prompt": "Complete: 'She ___ a teacher.'",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("is", True), ("are", False), ("am", False)]
    },

    # A2 — 5 вопросов
    {
        "prompt": "She is interested ___ music.",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("in", True), ("on", False), ("at", False)]
    },
    {
        "prompt": "They ___ tennis every week.",
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
        "prompt": "'She can ___ fast.'",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("run", True), ("slow", False), ("lazy", False)]
    },
    {
        "prompt": "Past tense of 'go'?",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("went", True), ("goed", False), ("gone", False)]
    },

    # B1 — 5 вопросов
    {
        "prompt": "'Difficult' means...",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("hard", True), ("easy", False), ("light", False)]
    },
    {
        "prompt": "I have been working ___ morning.",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("since", True), ("from", False), ("by", False)]
    },
    {
        "prompt": "'Good ___ math'",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("at", True), ("in", False), ("to", False)]
    },
    {
        "prompt": "Choose the correct question: ___ you like pizza?",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("Do", True), ("Does", False), ("Did", False)]
    },
    {
        "prompt": "Synonym of 'job'?",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("work", True), ("rest", False), ("play", False)]
    },

    # B2 — 5 вопросов
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
        "prompt": "Passive: The cake ___ baked.",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("was", True), ("is", False), ("has", False)]
    },
    {
        "prompt": "Choose correct form: 'He ___ been there.'",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("has", True), ("have", False), ("had", False)]
    },
    {
        "prompt": "Synonym of 'achieve'?",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("accomplish", True), ("avoid", False), ("fail", False)]
    },

    # C1 — 5 вопросов
    {
        "prompt": "'Were I you...' means?",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("If I were you", True), ("If I was you", False), ("If I'm you", False)]
    },
    {
        "prompt": "'Drop the ball' means?",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("fail", True), ("run", False), ("improve", False)]
    },
    {
        "prompt": "Subjunctive mood used in:",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("I wish I were rich", True), ("She is smart", False), ("I am here", False)]
    },
    {
        "prompt": "Synonym of 'complex'?",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("complicated", True), ("simple", False), ("clear", False)]
    },
    {
        "prompt": "'As though' is used to express?",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("hypothesis", True), ("certainty", False), ("request", False)]
    },

    # C2 — 5 вопросов
    {
        "prompt": "'By the skin of your teeth' means?",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("barely succeed", True), ("lose badly", False), ("cheat", False)]
    },
    {
        "prompt": "'Not only ___ he smart, but also kind.'",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("is", True), ("does", False), ("was", False)]
    },
    {
        "prompt": "Meaning of 'ephemeral'?",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("short-lived", True), ("eternal", False), ("boring", False)]
    },
        {
        "prompt": "'Hardly ___ she left when it rained.'",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("had", True), ("has", False), ("have", False)]
    },
    {
        "prompt": "'Throw in the towel' means?",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("give up", True), ("celebrate", False), ("try harder", False)]
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

