import argparse
import csv
import time
from datetime import datetime
from pathlib import Path

from quiz import LETTERS, ask_question, load_questions, shuffle_questions

RESULTS_FILE = Path(__file__).with_name("results.csv")


def prompt_count(total):
    """Ask how many questions to run; empty input means all of them."""
    while True:
        raw = input(f"How many questions? (default: all {total}): ").strip()
        if not raw:
            return total
        if raw.isdigit() and 1 <= int(raw) <= total:
            return int(raw)
        print(f"Please enter a number between 1 and {total}.")


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
    args = parser.parse_args()

    questions = shuffle_questions(load_questions())
    total = len(questions)

    if args.count is not None:
        if not 1 <= args.count <= total:
            parser.error(f"--count must be between 1 and {total}")
        count = args.count
    else:
        count = prompt_count(total)

    questions = questions[:count]
    score = 0
    start = time.time()

    for i, q in enumerate(questions, 1):
        print(f"\nQuestion {i} of {count}")
        if ask_question(q):
            print("Correct!")
            score += 1
        else:
            letter = LETTERS[q["correct_index"]]
            print(f"Wrong, the answer was {letter}) {q['options'][q['correct_index']]}")

    elapsed = time.time() - start
    percentage = round(score / count * 100)

    print(f"\nScore: {score}/{count}")
    print(f"Percentage: {percentage}%")
    print(f"Time taken: {elapsed:.1f} seconds")

    save_result(score, count, percentage)
    print(f"Result saved to {RESULTS_FILE}")


if __name__ == "__main__":
    main()
