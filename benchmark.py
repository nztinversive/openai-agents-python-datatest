import argparse
import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List

from csv_mcp.agents import build_analysis_agent
from csv_mcp.csv_loader import load_csv, preview_df
from agents import Runner, Usage


def lcs(a: List[str], b: List[str]) -> int:
    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i, ai in enumerate(a, 1):
        for j, bj in enumerate(b, 1):
            if ai == bj:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])
    return dp[-1][-1]


def rouge_l(pred: str, ref: str) -> float:
    pred_tokens = pred.split()
    ref_tokens = ref.split()
    if not pred_tokens or not ref_tokens:
        return 0.0
    lcs_len = lcs(pred_tokens, ref_tokens)
    precision = lcs_len / len(pred_tokens)
    recall = lcs_len / len(ref_tokens)
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o": {"input": 0.005 / 1000, "output": 0.015 / 1000},
    "gpt-4": {"input": 0.03 / 1000, "output": 0.06 / 1000},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
}


def estimate_cost(model: str, usage: Usage) -> float:
    pricing = _PRICING.get(model, {"input": 0.0, "output": 0.0})
    return usage.input_tokens * pricing["input"] + usage.output_tokens * pricing["output"]


async def run_pipeline(model: str, reference: str) -> Dict[str, Any]:
    df = load_csv("csv_mcp/input.csv")
    input_text = preview_df(df)
    agent = build_analysis_agent(model_name=model)

    start = time.perf_counter()
    result = await Runner.run(agent, input_text)
    elapsed = time.perf_counter() - start

    usage = result.context_wrapper.usage
    tokens = usage.total_tokens
    cost = estimate_cost(model, usage)
    rouge = rouge_l(str(result.final_output), reference)

    return {
        "model": model,
        "seconds": elapsed,
        "tokens": tokens,
        "cost": cost,
        "rouge_l": rouge,
    }


def print_table(results: List[Dict[str, Any]]) -> None:
    print("| Model | Seconds | Tokens | Cost (USD) | Rouge-L |")
    print("|-------|--------:|-------:|-----------:|--------:|")
    for r in results:
        print(
            f"| {r['model']} | {r['seconds']:.2f} | {r['tokens']} | $"
            f"{r['cost']:.4f} | {r['rouge_l']:.4f} |"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark multiple models")
    parser.add_argument("--models", nargs="+", required=True, help="List of model names")
    return parser.parse_args()


async def main() -> None:
    args = parse_args()
    reference = Path("truth_insights.md").read_text()
    results = []
    for model in args.models:
        metrics = await run_pipeline(model, reference)
        results.append(metrics)
    print_table(results)


if __name__ == "__main__":
    asyncio.run(main())
