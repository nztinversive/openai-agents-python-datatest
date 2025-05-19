from __future__ import annotations

import argparse
import asyncio

from agents import (
    Runner,
    build_aggregator_agent,
    build_analysis_agent,
    build_qna_agent,
    build_transform_agent,
)
from csv_loader import DataFrame, load_csv, write_csv


async def main() -> None:
    """Run the orchestration workflow."""
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path", help="Path to the CSV file to load.")
    parser.add_argument("--models", nargs="*", help="Optional list of model names.")
    args = parser.parse_args()

    data: DataFrame = load_csv(args.input_path)

    analysis_agent = build_analysis_agent(models=args.models)
    transform_agent = build_transform_agent(models=args.models)
    qna_agent = build_qna_agent(models=args.models)
    aggregator_agent = build_aggregator_agent(models=args.models)

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

    cleaned_df = agg_res.final_output.get("dataframe")
    insights = agg_res.final_output.get("insights")

    if cleaned_df is not None:
        write_csv(cleaned_df, "output.csv")
    if insights is not None:
        with open("insights.md", "w") as f:
            f.write(str(insights))

    print("output.csv")
    print("insights.md")


if __name__ == "__main__":
    asyncio.run(main())
