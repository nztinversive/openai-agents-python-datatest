from __future__ import annotations

from typing import Any

import pytest

from agents.fallback import retry_with_fallbacks


class DummyResult:
    def __init__(self, value: Any, confidence: float) -> None:
        self.value = value
        self.confidence = confidence


def test_retry_with_fallbacks_success(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []
    sleeps: list[float] = []

    def agent_call(model: str) -> DummyResult:
        calls.append(model)
        if model == "b":
            return DummyResult("ok", 0.9)
        return DummyResult("fail", 0.1)

    monkeypatch.setattr("agents.fallback.time.sleep", lambda x: sleeps.append(x))

    result = retry_with_fallbacks(agent_call, ["a", "b"], 0.8)

    assert result.value == "ok"
    assert calls == ["a", "b"]
    assert sleeps == [1.0]


def test_retry_with_fallbacks_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    sleeps: list[float] = []

    def agent_call(model: str) -> DummyResult:
        return DummyResult("bad", 0.1)

    monkeypatch.setattr("agents.fallback.time.sleep", lambda x: sleeps.append(x))

    with pytest.raises(RuntimeError):
        retry_with_fallbacks(agent_call, ["a", "b", "c"], 0.8)

    assert sleeps == [1.0, 2.0, 4.0]
