import asyncio
import json

import pytest

from agents import Runner
from agents.build import (
    build_analysis_agent,
    build_transform_agent,
    build_qna_agent,
    build_aggregator_agent,
)
from tests.fake_model import FakeModel
from tests.test_responses import get_text_message, get_final_output_message
from csv_loader import DataFrame


@pytest.mark.asyncio
async def test_agents_pipeline():
    data = DataFrame(rows=[{"a": 1}, {"a": 2}, {"a": 3}])

    analysis_agent = build_analysis_agent()
    transform_agent = build_transform_agent()
    qna_agent = build_qna_agent()
    aggregator_agent = build_aggregator_agent()

    analysis_agent.model = FakeModel()
    analysis_agent.model.set_next_output([get_text_message("analysis")])
    transform_agent.model = FakeModel()
    transform_agent.model.set_next_output([get_text_message("transform")])
    qna_agent.model = FakeModel()
    qna_agent.model.set_next_output([get_text_message("answer")])
    aggregator_agent.model = FakeModel()
    aggregator_agent.output_type = dict
    payload = json.dumps({"dataframe": {"rows": []}, "insights": "hi"})
    aggregator_agent.model.set_next_output([get_final_output_message(payload)])

    analysis_res, transform_res = await asyncio.gather(
        Runner.run(analysis_agent, data),
        Runner.run(transform_agent, data),
    )

    qna_input = {
        "analysis": analysis_res.final_output,
        "transform": transform_res.final_output,
    }
    qna_res = await Runner.run(qna_agent, qna_input)

    agg_input = {
        "analysis": analysis_res.final_output,
        "transform": transform_res.final_output,
        "qna": qna_res.final_output,
    }
    agg_res = await Runner.run(aggregator_agent, agg_input)

    assert set(agg_res.final_output.keys()) == {"dataframe", "insights"}
