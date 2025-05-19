import asyncio
import sys
from pathlib import Path
from typing import Any

import pytest

import orchestrator
from csv_loader import DataFrame
from agents import Agent, RunContextWrapper, RunResult


def _result(output: Any) -> RunResult:
    return RunResult(
        input="x",
        new_items=[],
        raw_responses=[],
        final_output=output,
        input_guardrail_results=[],
        output_guardrail_results=[],
        _last_agent=Agent(name="test"),
        context_wrapper=RunContextWrapper(context=None),
    )


@pytest.mark.asyncio
async def test_orchestrator_end_to_end(monkeypatch, tmp_path):
    csv_src = Path("tests/fixtures/sample.csv")
    csv_path = tmp_path / "sample.csv"
    csv_path.write_text(csv_src.read_text())
    monkeypatch.chdir(tmp_path)

    async def fake_run(cls, agent: Agent, input: Any, **_: Any) -> RunResult:
        if agent.name == "analysis_agent":
            return _result("analysis")
        if agent.name == "transform_agent":
            return _result("transform")
        if agent.name == "qna_agent":
            return _result("answer")
        if agent.name == "aggregator_agent":
            return _result({"dataframe": DataFrame(rows=[]), "insights": "insight"})
        raise AssertionError("unknown agent")

    monkeypatch.setattr(orchestrator.Runner, "run", classmethod(fake_run))

    printed: list[str] = []
    monkeypatch.setattr(orchestrator, "print", lambda x: printed.append(x))

    monkeypatch.setattr(sys, "argv", ["prog", str(csv_path)])
    await orchestrator.main()

    assert "output.csv" in printed
    assert "insights.md" in printed
    assert Path("output.csv").exists()
    assert Path("insights.md").exists()
