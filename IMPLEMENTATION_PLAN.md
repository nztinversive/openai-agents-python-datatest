# CSV Agent Pipeline: Implementation Plan

This document outlines the planned phases and steps to enhance the CSV processing pipeline, moving towards a more interactive, chat-driven, and AI-coordinated system using SDK Handoffs.

## Phase A: Handoff-Driven Task Delegation with Interactive Chat (High Priority)

*Goal: Replace the Python-level router with a primary agent that uses SDK Handoffs to delegate tasks to specialized agents. Implement an interactive chat loop with state management for this new architecture.*

1.  **Define/Update Agent Instructions and Handoff Configurations (in `src/agents/build.py`):**
    *   [ ] **`PrimaryInteractionAgent` (New Agent):**
        *   [ ] Create `build_primary_interaction_agent`.
        *   [ ] Instructions: Understand user's query about CSV data. Decide to answer directly (for simple greetings/meta-questions like "what can you do?") or handoff to a specialized agent (`analysis_agent`, `transform_agent`, `qna_agent`). Must provide necessary inputs for the handoff tool call.
        *   [ ] **Handoffs Setup**: Configure with `handoff()` objects for each specialized agent.
            *   [ ] **Handoff to `analysis_agent`**:
                *   [ ] `input_type` (Pydantic Model, e.g., `AnalysisHandoffInput`): May be empty if analysis always uses full dataset from history.
                *   [ ] `input_filter` (Optional): e.g., `handoff_filters.remove_all_tools`.
            *   [ ] **Handoff to `transform_agent`**:
                *   [ ] `input_type` (e.g., `TransformHandoffInput`): Must include `user_query_for_transform: str` for specific instructions.
                *   [ ] `input_filter` (Optional).
            *   [ ] **Handoff to `qna_agent`**:
                *   [ ] `input_type` (e.g., `QnAHandoffInput`): Must include `user_question: str`.
                *   [ ] `input_filter` (Optional).
        *   [ ] Add `RECOMMENDED_PROMPT_PREFIX` for handoffs to its instructions as per SDK docs.
    *   [ ] **Update Specialized Agent Instructions (`analysis_agent`, `transform_agent`, `qna_agent`):**
        *   [ ] Ensure their instructions clarify they will receive primary data context via conversation history and specific task details/parameters via the `input_data` from the handoff (the Pydantic model instance).
        *   [ ] `analysis_agent`: Operates on data from history.
        *   [ ] `transform_agent`: Uses `user_query_for_transform` from `input_data` and data from history. Output (JSON with `cleaned_data_csv_string`, `transform_summary`) remains the same.
        *   [ ] `qna_agent`: Uses `user_question` from `input_data` and data from history. Output (JSON with `response_type`, `answer`/`posed_questions_and_answers`) remains similar.
    *   [ ] Remove `build_router_agent` as its functionality is absorbed by `PrimaryInteractionAgent`.

2.  **Refactor `orchestrator.py` - `main()` function:**
    *   [ ] **Remove Router Logic**: Delete code related to calling `router_agent` and the subsequent `if/elif` dispatch.
    *   [ ] **Interactive Chat Loop**: 
        *   [ ] Load initial CSV data once into `initial_data_rows` (e.g., `list[dict]`).
        *   [ ] Initialize `current_conversation_messages: list[dict]` to store the history for `Runner.run`.
        *   [ ] **Initial System Message/Data Loading**: Add an initial user message to `current_conversation_messages` that contains the loaded CSV data as a JSON string. E.g., `{"role": "user", "content": [{"type": "input_text", "text": f"Here is the data we will be working with: {json.dumps(initial_data_rows)}"}]}`. This provides context to the `PrimaryInteractionAgent`.
        *   [ ] Implement `while True` loop for user input (`user_query`). Handle "quit".
    *   **Running `PrimaryInteractionAgent`**: 
        *   [ ] Add user's current `user_query` to `current_conversation_messages` (formatted as a user message dict).
        *   [ ] Call `result = await Runner.run(primary_interaction_agent, current_conversation_messages)`.
        *   [ ] Add the assistant's final output from `result.final_output` (and any tool calls/responses if we want to show them or if they are crucial for history) back to `current_conversation_messages` to maintain history for the next turn.
        *   [ ] Print `result.final_output` (which is the response from the last agent in the handoff chain) to the user.
    *   [ ] **State Management for Transformations (Crucial & Complex):**
        *   [ ] **Strategy**: After a `Runner.run` call where a transformation *might* have occurred (i.e., if the `PrimaryInteractionAgent` decided to hand off to `transform_agent` and it completed successfully):
            *   The `transform_agent`'s output is a JSON string containing `cleaned_data_csv_string`.
            *   The `result.final_output` (if the transform_agent was the last one) will be this JSON string.
            *   [ ] Parse this `result.final_output` to get `cleaned_data_csv_string`.
            *   [ ] If successful:
                *   Parse `cleaned_data_csv_string` into a new `list[dict]` (e.g., `transformed_rows`).
                *   Save to `output.csv`.
                *   **Update Context for Next Turn**: Modify `current_conversation_messages`. This is key. One way: Append a new system or user message summarizing the transformation and explicitly providing the new data, OR, more complexly, try to *replace* the old data message in the history. A simpler start: explicitly tell the user data was transformed and saved, and that for the *next interaction to use the transformed data*, they might need to state it or the system could be designed to *prefer* it. For true seamlessness, the `PrimaryInteractionAgent` needs to be aware. A practical approach: if a transform occurred, the *next* user message in `current_conversation_messages` that kicks off the call to `PrimaryInteractionAgent` could be prepended with a system message like: `{"role": "system", "content": [{"type": "input_text", "text": f"The data was just transformed. Here is the new data: {json.dumps(transformed_rows)}. Please use this for subsequent operations unless otherwise specified."}]}`.
                *   Or, more simply: `initial_data_rows` (the Python variable) gets updated, and the *next* initial data message implicitly uses this if we rebuild `current_conversation_messages` carefully. (This needs careful thought on how `Runner.run` uses the passed `messages_list` vs. internal history from handoffs).
    *   [ ] Remove `--query` CLI argument; input will come from the interactive loop. `input_path` remains. `--models` remains.

3.  **Testing and Iteration:**
    *   [ ] Test various queries to ensure correct handoff and data passing via `input_type` and history.
    *   [ ] Focus on the data transformation state update: does the `PrimaryInteractionAgent` correctly use the transformed data in subsequent handoffs within the same session?
    *   [ ] Refine prompts for `PrimaryInteractionAgent` and specialized agents for clarity and reliability of handoffs.

### Phase A.2 (was A.2 & A.3): Session Aggregation & Enhanced Robustness (Post Handoff Implementation)

*Goal: Allow users to generate a summary report and improve error handling.*

1.  **State for Aggregation (similar to old A.2):**
    *   [ ] `session_reports` list, populated after each specialized agent's successful execution (via handoff).
    *   [ ] Trigger aggregation via a user command (e.g., "summarize session"). `PrimaryInteractionAgent` could have a specific handoff or tool for this, or handle it directly.
2.  **Error Handling (similar to old A.3):**
    *   [ ] Output parsing, LLM API errors.
    *   [ ] `PrimaryInteractionAgent` uncertainty: Its LLM could be prompted to ask for clarification if it's unsure which handoff tool to use for the user's query.

## Phase B: Advanced Coordinator Agent (Future - Builds on `PrimaryInteractionAgent`)

*Goal: Enable the `PrimaryInteractionAgent` to plan and execute multi-step sequences based on a single complex user query, potentially by calling multiple handoff tools sequentially or by generating a plan that the orchestrator helps execute.*

1.  **Enhance `PrimaryInteractionAgent` Instructions & Logic:**
    *   [ ] Instruct it to decompose complex queries (e.g., "Analyze, then transform X, then answer Y about the transformed data") into a sequence of handoffs.
    *   [ ] The LLM driving `PrimaryInteractionAgent` would need to manage the sequence of tool (handoff) calls.
    *   [ ] This phase would heavily rely on the LLM's capability to reason about sequences and manage intermediate states/outputs from handoffs to feed into subsequent handoffs.
2.  **Data Flow Between Chained Handoffs:**
    *   [ ] Outputs from one specialized agent (e.g., `analysis_report`) need to be available in the `PrimaryInteractionAgent`'s context/history so it can correctly populate the `input_type` for the *next* handoff in a chain.
    *   [ ] The `Runner.run` loop and how it appends tool call results to history will be critical here.

This plan prioritizes getting the core handoff mechanism and interactive loop working first. 