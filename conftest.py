"""Puts the project root on sys.path so tests can import quiz and main,
and provides a shared fixture for mocking builtins.input."""
import builtins

import pytest


class FakeInput:
    """Stand-in for builtins.input that replays canned answers."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        return self.answers.pop(0)


@pytest.fixture()
def fake_input(monkeypatch):
    """Install a FakeInput for the given answers; returns it for assertions."""

    def _install(answers):
        fake = FakeInput(answers)
        monkeypatch.setattr(builtins, "input", fake)
        return fake

    return _install
