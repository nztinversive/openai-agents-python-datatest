from __future__ import annotations

from .agent import Agent


def build_analysis_agent(models: list[str] | None = None) -> Agent:
    """Return an agent that performs data analysis."""
    model = models[0] if models else None
    return Agent(name="analysis_agent", instructions="Analyze the provided data.", model=model)


def build_transform_agent(models: list[str] | None = None) -> Agent:
    """Return an agent that transforms data."""
    model = models[1] if models and len(models) > 1 else (models[0] if models else None)
    return Agent(name="transform_agent", instructions="Transform the provided data.", model=model)


def build_qna_agent(models: list[str] | None = None) -> Agent:
    """Return an agent that answers questions about the data."""
    model = models[2] if models and len(models) > 2 else (models[0] if models else None)
    return Agent(name="qna_agent", instructions="Answer questions about the data.", model=model)


def build_aggregator_agent(models: list[str] | None = None) -> Agent:
    """Return an agent that aggregates all insights."""
    model = models[3] if models and len(models) > 3 else (models[0] if models else None)
    return Agent(name="aggregator_agent", instructions="Aggregate all insights.", model=model)
