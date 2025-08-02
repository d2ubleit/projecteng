import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

import uuid
from sqlalchemy.orm import Session
from backend.database.database import SessionLocal
from backend.app.models import DragItem, DropTarget, Question, Option, EnglishLevel, QuestionType, QuestionCategory

QUESTIONS = [
    # A1 — 6 вопросов
    {
        "prompt": "Translate the word 'apple'.",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Apple", True), ("Banana", False), ("Orange", False)]
    },
    {
        "prompt": "Complete: 'I ___ a student.'",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("am", True), ("is", False), ("are", False)]
    },
    {
        "prompt": "Choose the correct article: ___ cat is sleeping.",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("The", True), ("A", False), ("An", False)]
    },
    {
        "prompt": "Which one is a color?",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Blue", True), ("Chair", False), ("Run", False)]
    },
    {
        "prompt": "What is the opposite of 'hot'?",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Cold", True), ("Warm", False), ("Boil", False)]
    },
    {
        "prompt": "Choose the correct verb: 'She ___ to school.'",
        "level": EnglishLevel.A1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("goes", True), ("go", False), ("gone", False)]
    },

    # A2 — 6 вопросов
    {
        "prompt": "Choose the correct preposition: 'He is good ___ math.'",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("at", True), ("in", False), ("to", False)]
    },
    {
        "prompt": "Which word means 'quick'?",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Fast", True), ("Slow", False), ("Lazy", False)]
    },
    {
        "prompt": "Choose the correct form: 'They ___ dinner now.'",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("are having", True), ("have", False), ("has", False)]
    },
    {
        "prompt": "What is the past tense of 'buy'?",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("bought", True), ("buyed", False), ("buys", False)]
    },
    {
        "prompt": "Choose the synonym of 'happy'.",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Joyful", True), ("Sad", False), ("Angry", False)]
    },
    {
        "prompt": "Complete: 'I have lived here ___ 2010.'",
        "level": EnglishLevel.A2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("since", True), ("for", False), ("from", False)]
    },

    # B1 — 6 вопросов
    {
        "prompt": "Choose the correct question: ___ you ever been abroad?",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("Have", True), ("Did", False), ("Do", False)]
    },
    {
        "prompt": "What does 'generous' mean?",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Kind and giving", True), ("Mean", False), ("Lazy", False)]
    },
    {
        "prompt": "Choose the correct sentence: 'I ___ my homework before dinner.'",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("finished", True), ("finish", False), ("finishing", False)]
    },
    {
        "prompt": "Synonym of 'important'?",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Significant", True), ("Tiny", False), ("Optional", False)]
    },
    {
        "prompt": "Choose the correct form: 'She ___ working here for years.'",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("has been", True), ("is", False), ("was", False)]
    },
    {
        "prompt": "What is the opposite of 'cheap'?",
        "level": EnglishLevel.B1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("Expensive", True), ("Free", False), ("Small", False)]
    },
]

QUESTIONS += [
    # B2 — 6 вопросов
    {
        "prompt": "What is the synonym of 'assist'?",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("help", True), ("ignore", False), ("delay", False)]
    },
    {
        "prompt": "Complete the sentence: 'He ___ finished the report.'",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.open_text,
        "correct_answer": "has"
    },
    {
        "prompt": "Match the phrasal verbs to their meanings.",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.drag_and_drop,
        "drag_items": [
            {"text": "give up", "target_key": "quit"},
            {"text": "look after", "target_key": "care"},
            {"text": "run into", "target_key": "meet"}
        ],
        "drop_targets": ["quit", "care", "meet"]
    },
    {
        "prompt": "Choose the correct passive form: 'The book ___ written by her.'",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("was", True), ("is", False), ("has", False)]
    },
    {
        "prompt": "Translate 'успех' to English.",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.open_text,
        "correct_answer": "success"
    },
    {
        "prompt": "Match the countries to their continents.",
        "level": EnglishLevel.B2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.drag_and_drop,
        "drag_items": [
            {"text": "Brazil", "target_key": "South America"},
            {"text": "Germany", "target_key": "Europe"},
            {"text": "Japan", "target_key": "Asia"}
        ],
        "drop_targets": ["South America", "Europe", "Asia"]
    },

    # C1 — 6 вопросов
    {
        "prompt": "What does 'meticulous' mean?",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.open_text,
        "correct_answer": "careful"
    },
    {
        "prompt": "Match the idioms to their meanings.",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.drag_and_drop,
        "drag_items": [
            {"text": "break the ice", "target_key": "start conversation"},
            {"text": "hit the sack", "target_key": "go to bed"},
            {"text": "spill the beans", "target_key": "reveal secret"}
        ],
        "drop_targets": ["start conversation", "go to bed", "reveal secret"]
    },
    {
        "prompt": "Choose the correct form: 'Had I known, I ___ have helped.'",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.multiple_choice,
        "options": [("would", True), ("will", False), ("can", False)]
    },
    {
        "prompt": "Translate 'предложение' (в смысле grammar) to English.",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.open_text,
        "correct_answer": "sentence"
    },
    {
        "prompt": "Match the connectors to their functions.",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.grammar,
        "type": QuestionType.drag_and_drop,
        "drag_items": [
            {"text": "however", "target_key": "contrast"},
            {"text": "therefore", "target_key": "result"},
            {"text": "moreover", "target_key": "addition"}
        ],
        "drop_targets": ["contrast", "result", "addition"]
    },
    {
        "prompt": "Choose the correct word: 'He is ___ to succeed.'",
        "level": EnglishLevel.C1,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("likely", True), ("maybe", False), ("possibly", False)]
    },

    # C2 — 6 вопросов
    {
        "prompt": "Translate 'мимолетный' to English.",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.open_text,
        "correct_answer": "ephemeral"
    },
    {
        "prompt": "Match the advanced words to their definitions.",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.drag_and_drop,
        "drag_items": [
            {"text": "ubiquitous", "target_key": "everywhere"},
            {"text": "ambiguous", "target_key": "unclear"},
            {"text": "benevolent", "target_key": "kind"}
        ],
        "drop_targets": ["everywhere", "unclear", "kind"]
    },
    {
        "prompt": "Choose the correct word: 'Her argument was highly ___.'",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("persuasive", True), ("aggressive", False), ("confusing", False)]
    },
    {
        "prompt": "Translate 'предвзятый' to English.",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.open_text,
        "correct_answer": "biased"
    },
    {
        "prompt": "Match the Latin phrases to their meanings.",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.drag_and_drop,
        "drag_items": [
            {"text": "carpe diem", "target_key": "seize the day"},
            {"text": "et cetera", "target_key": "and so on"},
            {"text": "vice versa", "target_key": "the other way around"}
        ],
        "drop_targets": ["seize the day", "and so on", "the other way around"]
    },
    {
        "prompt": "Choose the correct word: 'His style is ___ and elegant.'",
        "level": EnglishLevel.C2,
        "category": QuestionCategory.vocabulary,
        "type": QuestionType.multiple_choice,
        "options": [("refined", True), ("rough", False), ("basic", False)]
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

        if q["type"] == QuestionType.open_text:
            question.correct_answer = q["correct_answer"]

        db.add(question)
        db.commit()
        db.refresh(question)

        if q["type"] == QuestionType.multiple_choice:
            for text, correct in q["options"]:
                db.add(Option(
                    question_id=question.id,
                    text=text,
                    is_correct=correct
                ))

        elif q["type"] == QuestionType.drag_and_drop:
            for item in q["drag_items"]:
                db.add(DragItem(
                    question_id=question.id,
                    label=item["text"],
                    target_key=item["target_key"]
                ))
            for target in q["drop_targets"]:
                db.add(DropTarget(
                    question_id=question.id,
                    target_key=target,
                    placeholder=target
                ))

        db.commit()

    print("✅ Все вопросы загружены в базу данных")


if __name__ == "__main__":
    seed_questions()

