import json
import random
from pathlib import Path

QUESTIONS_FILE = Path(__file__).with_name("questions.json")
LETTERS = ["a", "b", "c", "d"]


def load_questions():
    """Read the quiz questions from questions.json."""
    with open(QUESTIONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def shuffle_questions(questions):
    """Return the questions in random order with randomly ordered options.

    Each question is rebuilt as a new dict whose correct_index points at
    the new position of the original correct answer.
    """
    shuffled = random.sample(questions, len(questions))
    result = []
    for q in shuffled:
        correct_text = q["options"][q["correct_index"]]
        options = q["options"][:]
        random.shuffle(options)
        result.append({
            "question": q["question"],
            "options": options,
            "correct_index": options.index(correct_text),
        })
    return result


def ask_question(question_dict):
    """Print the question with lettered options, read an answer, return True if correct."""
    print(question_dict["question"])
    for letter, option in zip(LETTERS, question_dict["options"]):
        print(f"  {letter}) {option}")

    while True:
        answer = input("Your answer (a/b/c/d): ").strip().lower()
        if answer in LETTERS:
            break
        print("Please enter a, b, c, or d.")

    return LETTERS.index(answer) == question_dict["correct_index"]


def main():
    questions = shuffle_questions(load_questions())
    score = 0
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i} of {len(questions)}")
        if ask_question(q):
            print("Correct!")
            score += 1
        else:
            correct_letter = LETTERS[q["correct_index"]]
            print(f"Wrong! The correct answer was {correct_letter}) {q['options'][q['correct_index']]}")
    print(f"\nYou scored {score} out of {len(questions)}.")


if __name__ == "__main__":
    main()
