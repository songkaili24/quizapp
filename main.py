import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

from quiz import LETTERS, get_answer_letter, load_questions, shuffle_questions

RESULTS_FILE = Path(__file__).with_name("results.csv")


def filter_by_category(questions, category):
    """Return questions whose category matches (case-insensitive)."""
    wanted = category.strip().lower()
    filtered = [q for q in questions if q.get("category", "").lower() == wanted]
    if not filtered:
        available = sorted({q.get("category", "Uncategorized") for q in questions})
        raise SystemExit(
            f"No questions in category '{category}'. "
            f"Available categories: {', '.join(available)}"
        )
    return filtered


def prompt_count(total):
    """Ask how many questions to run; empty input means all of them."""
    while True:
        raw = input(f"How many questions? (default: all {total}): ").strip()
        if not raw:
            return total
        if raw.isdigit() and 1 <= int(raw) <= total:
            return int(raw)
        print(f"Please enter a number between 1 and {total}.")


def run_quiz(questions):
    """Ask each question once; return (score, wrong_answers, elapsed_seconds).

    wrong_answers is a list of (question_dict, user_letter) pairs.
    """
    score = 0
    wrong = []
    start = time.time()
    count = len(questions)
    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i} of {count}")
        print(q["question"])
        for letter, option in zip(LETTERS, q["options"]):
            print(f"  {letter}) {option}")

        letter = get_answer_letter()
        if LETTERS.index(letter) == q["correct_index"]:
            print("Correct!")
            score += 1
        else:
            correct_idx = q["correct_index"]
            print(f"Wrong, the answer was {LETTERS[correct_idx]}) {q['options'][correct_idx]}")
            wrong.append((q, letter))
    elapsed = time.time() - start
    return score, wrong, elapsed


def print_review(wrong):
    """Print a table of the wrongly answered questions."""
    if not wrong:
        print("\nPerfect score - nothing to review!")
        return

    headers = ("Question", "Your answer", "Correct answer")
    rows = []
    for q, user_letter in wrong:
        user_idx = LETTERS.index(user_letter)
        correct_idx = q["correct_index"]
        question = q["question"]
        if len(question) > 45:
            question = question[:42] + "..."
        rows.append((
            question,
            f"{user_letter}) {q['options'][user_idx]}",
            f"{LETTERS[correct_idx]}) {q['options'][correct_idx]}",
        ))

    widths = [max(len(headers[c]), max(len(r[c]) for r in rows)) for c in range(3)]
    header_line = "  ".join(headers[c].ljust(widths[c]) for c in range(3))
    print("\nReview of wrong answers:")
    print(header_line)
    print("-" * len(header_line))
    for r in rows:
        print("  ".join(cell.ljust(widths[c]) for c, cell in enumerate(r)))


def save_result(score, total, percentage):
    """Append one row to results.csv, writing the header on first use."""
    is_new = not RESULTS_FILE.exists()
    with open(RESULTS_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if is_new:
            writer.writerow(["Date", "Score", "Total", "Percentage"])
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            score,
            total,
            percentage,
        ])


def main():
    parser = argparse.ArgumentParser(description="Run the quiz app.")
    parser.add_argument("--count", type=int, metavar="N",
                        help="number of questions to ask (skips the prompt)")
    parser.add_argument("--category", metavar="NAME",
                        help="only ask questions from this category (case-insensitive)")
    parser.add_argument("--review", action="store_true",
                        help="after the quiz, print a table of wrong answers")
    args = parser.parse_args()

    questions = load_questions()
    if args.category:
        questions = filter_by_category(questions, args.category)
    questions = shuffle_questions(questions)
    total = len(questions)

    if args.count is not None:
        if not 1 <= args.count <= total:
            parser.error(f"--count must be between 1 and {total}")
        count = args.count
    else:
        count = prompt_count(total)

    score, wrong, elapsed = run_quiz(questions[:count])
    percentage = round(score / count * 100)

    print(f"\nScore: {score}/{count}")
    print(f"Percentage: {percentage}%")
    print(f"Time taken: {elapsed:.1f} seconds")

    save_result(score, count, percentage)
    print(f"Result saved to {RESULTS_FILE}")

    if args.review:
        print_review(wrong)


if __name__ == "__main__":
    main()
