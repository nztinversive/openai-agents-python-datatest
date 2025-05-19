from __future__ import annotations

import argparse
import asyncio
import json
from typing import Any, Dict, List

from agents import Runner
from csv_mcp.agents import (
    build_primary_interaction_agent,
    TransformOutput,
    AnalysisOutput,
    QnAOutput,
)
from csv_loader import load_csv, write_csv, csv_string_to_dataframe, dataframe_to_csv_string


async def main() -> None:
    """Run the interactive CSV agent orchestration workflow."""
    parser = argparse.ArgumentParser(description="Interactive CSV Agent Orchestrator")
    parser.add_argument("input_path", help="Path to the initial CSV file to load.")
    parser.add_argument(
        "--models",
        nargs="*",
        help="Optional list of model names for agents, e.g., primary=gpt-4-o analysis=o3-mini. "
             "Supported keys: primary, analysis, transform, qna."
    )
    args = parser.parse_args()

    models_config = {}
    if args.models:
        for model_arg in args.models:
            if "=" in model_arg:
                key, value = model_arg.split("=", 1)
                models_config[key.lower()] = value
            else:
                print(f"Warning: Model argument '{model_arg}' lacks a key; ignoring. Use key=value format.")

    primary_agent = build_primary_interaction_agent(
        primary_interaction_model=models_config.get("primary", "gpt-4.1"),
        analysis_agent_model=models_config.get("analysis", "o3"),
        transform_agent_model=models_config.get("transform", "o3"),
        qna_agent_model=models_config.get("qna", "gpt-4.1"),
    )

    try:
        current_data_rows: List[Dict[str, Any]] = load_csv(args.input_path)
        print(f"Successfully loaded {len(current_data_rows)} rows from {args.input_path}")
    except Exception as e:
        print(f"Error loading CSV from {args.input_path}: {e}")
        return

    initial_data_message_content = f"Here is the data we will be working with: {json.dumps(current_data_rows)}"
    current_conversation_messages: list[dict] = [
        {"role": "user", "content": initial_data_message_content}
    ]
    
    session_reports: List[Dict[str, Any]] = []

    print("Starting interactive CSV agent. Type 'quit' to exit, or 'summarize session' for a report.")

    while True:
        try:
            user_query = input("\nUser: ").strip()
            if user_query.lower() == "quit":
                print("Exiting...")
                break
            if not user_query:
                continue
            
            if user_query.lower() == "summarize session":
                if not session_reports:
                    print("Assistant: No reports generated yet in this session.")
                    continue
                
                summary_request_message = "Please summarize the following session reports."
                reports_message_content = f"Here are the session reports to summarize: {json.dumps(session_reports)}"
                
                summary_messages = [
                    {"role": "system", "content": reports_message_content},
                    {"role": "user", "content": summary_request_message}
                ]

                print("Agent is generating session summary...")
                result = await Runner.run(primary_agent, current_conversation_messages + summary_messages)
                assistant_response = result.final_output
                print(f"Assistant (Summary): {assistant_response}")
                continue

            current_conversation_messages.append({"role": "user", "content": user_query})

            print("Agent is thinking...")
            result = await Runner.run(primary_agent, current_conversation_messages)
            assistant_response = result.final_output

            display_response_str = ""
            
            if isinstance(assistant_response, TransformOutput):
                display_response_str = f"Transformation Applied: {assistant_response.transform_summary}"
                print(f"Assistant: {display_response_str}")
                session_reports.append({"type": "transform", "summary": assistant_response.transform_summary, "data_preview (first 2 rows)": csv_string_to_dataframe(assistant_response.cleaned_data_csv_string)[:2]})
                
                new_data_rows = csv_string_to_dataframe(assistant_response.cleaned_data_csv_string)
                current_data_rows = new_data_rows
                output_file = "output.csv"
                write_csv(current_data_rows, output_file)
                print(f"Transformed data saved to {output_file}")
                transformed_data_message = f"The data was just transformed. Here is the new data: {json.dumps(current_data_rows)}. Please use this for subsequent operations unless otherwise specified."
                current_conversation_messages.append({"role": "system", "content": transformed_data_message})
                print("(System: Conversation context updated with transformed data.)")
            
            elif isinstance(assistant_response, AnalysisOutput):
                display_response_str = f"Analysis Complete: {assistant_response.analysis_summary}"
                print(f"Assistant: {display_response_str}")
                session_reports.append({"type": "analysis", "summary": assistant_response.analysis_summary})
            
            elif isinstance(assistant_response, QnAOutput):
                if assistant_response.answer:
                    display_response_str = f"Answer: {assistant_response.answer}"
                elif assistant_response.posed_questions_and_answers:
                    display_response_str = f"Q&A Elaboration: {json.dumps(assistant_response.posed_questions_and_answers)}"
                else:
                    display_response_str = f"Q&A Response Type: {assistant_response.response_type}"
                print(f"Assistant: {display_response_str}")
                session_reports.append({"type": "qna", "response_type": assistant_response.response_type, "details": assistant_response.model_dump()})
            
            elif isinstance(assistant_response, str):
                display_response_str = assistant_response
                print(f"Assistant: {display_response_str}")
            
            else:
                display_response_str = str(assistant_response)
                print(f"Assistant (Unknown Format): {display_response_str}")

            current_conversation_messages.append({"role": "assistant", "content": display_response_str})

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())
