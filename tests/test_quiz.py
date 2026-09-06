import quiz


def test_load_questions_valid():
    questions = quiz.load_questions()
    assert len(questions) >= 10
    for q in questions:
        assert isinstance(q["question"], str) and q["question"]
        assert len(q["options"]) == 4
        assert 0 <= q["correct_index"] <= 3
        assert isinstance(q["category"], str) and q["category"]


def test_shuffle_preserves_correct_answer():
    questions = quiz.load_questions()
    correct = {q["question"]: q["options"][q["correct_index"]] for q in questions}
    for _ in range(50):
        for q in quiz.shuffle_questions(questions):
            assert q["options"][q["correct_index"]] == correct[q["question"]]


def test_shuffle_changes_order():
    questions = quiz.load_questions()
    orders = {
        tuple(q["question"] for q in quiz.shuffle_questions(questions))
        for _ in range(20)
    }
    assert len(orders) > 1


def test_ask_question_correct(fake_input):
    q = quiz.load_questions()[0]
    fake_input([quiz.LETTERS[q["correct_index"]]])
    assert quiz.ask_question(q) is True


def test_ask_question_wrong(fake_input):
    q = quiz.load_questions()[0]
    wrong_letter = quiz.LETTERS[(q["correct_index"] + 1) % 4]
    fake_input([wrong_letter])
    assert quiz.ask_question(q) is False


def test_ask_question_invalid_input_reprompted_without_penalty(fake_input):
    q = quiz.load_questions()[0]
    letter = quiz.LETTERS[q["correct_index"]]
    # Junk input ("e", "abc", empty, whitespace) re-prompts; the eventual
    # correct answer still counts, so no answer is consumed by the junk.
    fake = fake_input(["e", "abc", "", "  ", letter.upper()])
    assert quiz.ask_question(q) is True
    assert len(fake.prompts) == 5


def test_get_answer_letter_accepts_uppercase(fake_input):
    fake = fake_input(["C"])
    assert quiz.get_answer_letter() == "c"
    assert len(fake.prompts) == 1
