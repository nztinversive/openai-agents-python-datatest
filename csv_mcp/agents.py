from __future__ import annotations

from typing import Optional

from agents import Agent


def build_analysis_agent(model_name: str = "o3") -> Agent:
    """Return an agent that analyzes CSV data."""
    return Agent(
        name="analysis_agent",
        instructions="Analyze the provided CSV data for insights and anomalies.",
        model=model_name,
    )


def build_transform_agent(model_name: str = "o3") -> Agent:
    """Return an agent that transforms CSV data."""
    return Agent(
        name="transform_agent",
        instructions="Transform raw CSV data into a normalized format.",
        model=model_name,
    )


def build_qna_agent(primary: str = "gpt-4.1", fallbacks: Optional[list[str]] = None) -> Agent:
    """Return a question answering agent for the CSV data."""
    _ = fallbacks  # Placeholder for future fallback support.
    return Agent(
        name="qna_agent",
        instructions="Answer questions about the CSV data.",
        model=primary,
    )


def build_aggregator_agent(model_name: str = "gpt-4.1") -> Agent:
    """Return an agent that aggregates outputs from other agents."""
    return Agent(
        name="aggregator_agent",
        instructions="Aggregate analysis and transformations into a single output.",
        model=model_name,
    )


def build_coordinator(
    analysis: Agent,
    transform: Agent,
    qna: Agent,
    aggregator: Agent,
) -> Agent:
    """Return a coordinator agent that delegates tasks to sub agents."""
    return Agent(
        name="coordinator_agent",
        instructions=(
            "Route the request to the appropriate sub agent. Use analysis for CSV"
            " review, transform for data conversion, qna for answering questions,"
            " and aggregator to combine results."
        ),
        handoffs=[analysis, transform, qna, aggregator],
    )
