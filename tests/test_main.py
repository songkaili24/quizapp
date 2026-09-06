import pytest

import main
import quiz

Q_MATH = {
    "question": "2 + 2?",
    "options": ["3", "4", "5", "22"],
    "correct_index": 1,
    "category": "Math",
}
Q_GEO = {
    "question": "Capital of France?",
    "options": ["Paris", "Berlin", "Madrid", "Rome"],
    "correct_index": 0,
    "category": "Geography",
}


def test_run_quiz_scores_mixed_answers(fake_input):
    fake_input(["b", "a"])  # correct for Q_MATH, correct for Q_GEO
    score, wrong, elapsed = main.run_quiz([Q_MATH, Q_GEO])
    assert score == 2
    assert wrong == []
    assert elapsed >= 0


def test_run_quiz_records_wrong_answers(fake_input):
    fake_input(["b", "d"])  # correct for Q_MATH, wrong for Q_GEO
    score, wrong, _ = main.run_quiz([Q_MATH, Q_GEO])
    assert score == 1
    assert wrong == [(Q_GEO, "d")]


def test_run_quiz_all_wrong(fake_input):
    fake_input(["a", "b"])  # both wrong
    score, wrong, _ = main.run_quiz([Q_MATH, Q_GEO])
    assert score == 0
    assert [w[0] for w in wrong] == [Q_MATH, Q_GEO]


def test_filter_by_category_case_insensitive():
    science = main.filter_by_category(quiz.load_questions(), "sCiEnCe")
    assert len(science) == 3
    assert all(q["category"] == "Science" for q in science)


def test_filter_by_category_unknown_exits_with_available_list():
    with pytest.raises(SystemExit) as excinfo:
        main.filter_by_category(quiz.load_questions(), "Sports")
    assert "No questions in category 'Sports'" in str(excinfo.value.code)
    assert "Available categories" in str(excinfo.value.code)


def test_print_review_shows_question_answers_correct(capsys):
    wrong = [(Q_GEO, "d")]  # answered Rome, correct is Paris
    main.print_review(wrong)
    out = capsys.readouterr().out
    assert "Question" in out and "Your answer" in out and "Correct answer" in out
    assert "Capital of France?" in out
    assert "d) Rome" in out
    assert "a) Paris" in out


def test_print_review_truncates_long_questions(capsys):
    long_q = dict(Q_MATH, question="A" * 100)
    main.print_review([(long_q, "a")])
    out = capsys.readouterr().out
    assert "A" * 42 + "..." in out
    assert "A" * 100 not in out


def test_print_review_perfect_score(capsys):
    main.print_review([])
    assert "Perfect score" in capsys.readouterr().out


def test_save_result_appends_with_single_header(tmp_path, monkeypatch):
    results = tmp_path / "results.csv"
    monkeypatch.setattr(main, "RESULTS_FILE", results)
    main.save_result(8, 10, 80)
    main.save_result(5, 10, 50)
    lines = results.read_text(encoding="utf-8").strip().splitlines()
    assert lines[0] == "Date,Score,Total,Percentage"
    assert len(lines) == 3
    assert lines[1].endswith(",8,10,80")
    assert lines[2].endswith(",5,10,50")


def test_main_end_to_end_perfect_score(fake_input, capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(main, "RESULTS_FILE", tmp_path / "results.csv")
    monkeypatch.setattr(main, "shuffle_questions", lambda qs: list(qs))
    monkeypatch.setattr("sys.argv", ["main.py", "--category", "Science",
                                     "--count", "2", "--review"])
    # Science questions in file order: Red Planet (b) and photosynthesis (b).
    fake_input(["b", "b"])
    main.main()
    out = capsys.readouterr().out
    assert "Score: 2/2" in out
    assert "Percentage: 100%" in out
    assert "Perfect score - nothing to review!" in out
    assert (tmp_path / "results.csv").read_text().strip().endswith(",2,2,100")


def test_main_end_to_end_review_table(fake_input, capsys, monkeypatch, tmp_path):
    monkeypatch.setattr(main, "RESULTS_FILE", tmp_path / "results.csv")
    monkeypatch.setattr(main, "shuffle_questions", lambda qs: list(qs))
    monkeypatch.setattr("sys.argv", ["main.py", "--category", "Science",
                                     "--count", "2", "--review"])
    fake_input(["a", "a"])  # both wrong
    main.main()
    out = capsys.readouterr().out
    assert "Score: 0/2" in out
    assert "Review of wrong answers" in out
    assert "a) Venus" in out and "b) Mars" in out
    assert "a) Oxygen" in out and "b) Carbon dioxide" in out
