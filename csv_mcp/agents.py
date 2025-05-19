from __future__ import annotations

from typing import Optional, List, Dict, Any

from agents import Agent, handoff
from agents.extensions.handoff_prompt import RECOMMENDED_PROMPT_PREFIX
from pydantic import BaseModel

# --- Pydantic Models for Handoff Inputs ---
class AnalysisHandoffInput(BaseModel):
    """Input for analysis_agent handoff. Currently empty as analysis uses full dataset from history."""
    pass

class TransformHandoffInput(BaseModel):
    """Input for transform_agent handoff."""
    user_query_for_transform: str

class QnAHandoffInput(BaseModel):
    """Input for qna_agent handoff."""
    user_question: str

# --- Pydantic Models for Agent Outputs ---
class TransformOutput(BaseModel):
    """Output model for transform_agent."""
    cleaned_data_csv_string: str
    transform_summary: str

class AnalysisOutput(BaseModel):
    """Output model for analysis_agent."""
    analysis_summary: str
    # Example: could also include more structured data like:
    # anomalies_found: List[str] = [] 
    # key_insights: List[str] = []

class QnAOutput(BaseModel):
    """Output model for qna_agent."""
    response_type: str # E.g., "answer", "clarification_needed", "cannot_answer"
    answer: Optional[str] = None
    posed_questions_and_answers: Optional[List[Dict[str, str]]] = None # For when it poses and answers its own clarificatory q's
    # error_message: Optional[str] = None # If cannot_answer or error

# --- Agent Builder Functions ---

def build_analysis_agent(model_name: str = "o3") -> Agent:
    """Return an agent that analyzes CSV data."""
    return Agent(
        name="analysis_agent",
        instructions="You are an expert data analyst. Analyze the provided CSV data (from conversation history) for insights and anomalies. "
                     "Focus on the data itself. The user may provide specific instructions via the handoff input. "
                     "Your output MUST conform to the AnalysisOutput schema, providing an 'analysis_summary'.",
        model=model_name,
        output_type=AnalysisOutput,
    )

def build_transform_agent(model_name: str = "o3") -> Agent:
    """Return an agent that transforms CSV data."""
    return Agent(
        name="transform_agent",
        instructions="You are an expert data transformer. Transform the raw CSV data (from conversation history) based on the user's request provided in the input. "
                     "Your output MUST conform to the TransformOutput schema, providing 'cleaned_data_csv_string' and 'transform_summary'.",
        model=model_name,
        output_type=TransformOutput,
    )

def build_qna_agent(primary_model: str = "gpt-4.1", fallbacks: Optional[list[str]] = None) -> Agent:
    """Return a question answering agent for the CSV data."""
    _ = fallbacks
    return Agent(
        name="qna_agent",
        instructions="You are a helpful Q&A assistant. Answer questions based on the provided CSV data (from conversation history) and the specific user question from the input. "
                     "Your output MUST conform to the QnAOutput schema, providing 'response_type' and 'answer' or other relevant fields.",
        model=primary_model,
        output_type=QnAOutput,
    )

def build_primary_interaction_agent(
    analysis_agent_model: str = "o3",
    transform_agent_model: str = "o3",
    qna_agent_model: str = "gpt-4.1",
    primary_interaction_model: str = "gpt-4.1",
) -> Agent:
    """Builds the primary agent that interacts with the user and delegates tasks via handoffs."""

    analysis_agent = build_analysis_agent(model_name=analysis_agent_model)
    transform_agent = build_transform_agent(model_name=transform_agent_model)
    qna_agent = build_qna_agent(primary_model=qna_agent_model)

    instructions = (
        "You are the primary assistant for interacting with users about their CSV data. "
        "Understand the user's query. You can answer simple greetings or meta-questions (e.g., 'what can you do?', 'hello'). "
        "For data-related tasks, you MUST decide whether to handoff to a specialized agent: "
        "1. 'analysis_agent': For requests to analyze, summarize, or find insights in the current dataset. "
        "2. 'transform_agent': For requests to modify, clean, filter, or reformat the current dataset. You must provide the user's specific transformation instruction in the 'user_query_for_transform' field. "
        "3. 'qna_agent': For specific questions about the data that require looking up or calculating answers from the current dataset. You must provide the user's question in the 'user_question' field. "
        "The CSV data itself will be available in the conversation history. "
        "If the user asks to 'summarize session' or 'generate report', and you see a system message in the history containing 'session_reports', "
        "provide a concise summary of these reports. Do not try to handoff for this specific task. "
        "If you are unsure about other tasks, ask for clarification. "
        f"{RECOMMENDED_PROMPT_PREFIX}"
    )
    
    # Define a dummy callable for on_handoff
    noop_handoff_callback = lambda *args, **kwargs: None

    return Agent(
        name="PrimaryInteractionAgent",
        instructions=instructions,
        model=primary_interaction_model,
        handoffs=[
            handoff(
                agent=analysis_agent,
                input_type=AnalysisHandoffInput,
                on_handoff=noop_handoff_callback, # Using dummy callable
            ),
            handoff(
                agent=transform_agent,
                input_type=TransformHandoffInput,
                on_handoff=noop_handoff_callback, # Using dummy callable
            ),
            handoff(
                agent=qna_agent,
                input_type=QnAHandoffInput,
                on_handoff=noop_handoff_callback, # Using dummy callable
            ),
        ],
    )

# Example of how agents might be built and passed to orchestrator
# This part would typically be in the orchestrator or main script

# def get_all_agents(models_config: Optional[dict] = None):
#     if models_config is None:
#         models_config = {}

#     primary_interaction_agent = build_primary_interaction_agent(
#         analysis_agent_model=models_config.get("analysis", "o3-mini"),
#         transform_agent_model=models_config.get("transform", "o3-mini"),
#         qna_agent_model=models_config.get("qna", "gpt-4-turbo-preview"),
#         primary_interaction_model=models_config.get("primary", "gpt-4-turbo-preview")
#     )
#     return primary_interaction_agent
