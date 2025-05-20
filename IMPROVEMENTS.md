# CSV-MCP Application: Potential Enhancements

This document outlines potential areas for improving the CSV-MCP (CSV Multi-Agent Coordinated Processing) application beyond its current implementation.

## 1. Enhanced Error Handling & Robustness (Completing Phase A.2 of original plan)

*   **Specific Error Catching in `orchestrator.py`**:
    *   Catch more specific exceptions from `Runner.run()` (e.g., API errors, network issues) and provide better user feedback or retry mechanisms.
    *   Gracefully handle cases where `result.final_output` is `None` or not the expected Pydantic model, even with `output_type`.
    *   *Likely files to edit: `orchestrator.py`*
*   **Input Validation for CSV**:
    *   Add robust checks in `csv_loader.py` or early in `orchestrator.py` for empty CSVs, inconsistent headers, or unexpected formats.
    *   *Likely files to edit: `csv_loader.py`, `orchestrator.py`*
*   **Refined Clarification from `PrimaryInteractionAgent`**:
    *   Improve instructions for the `PrimaryInteractionAgent` to be more proactive in asking for clarification if a user's query is too ambiguous for a confident handoff.
    *   *Likely files to edit: `csv_mcp/agents.py` (specifically the instructions for `build_primary_interaction_agent`)*

## 2. Improved User Experience (UX)

*   **Clearer "Thinking" Indicators**:
    *   Provide more contextual feedback during agent operations, especially if handoffs occur (e.g., "Analyzing data...", "Preparing transformation..."). This might involve changes to how `PrimaryInteractionAgent` signals its intent or how `orchestrator.py` interprets intermediate steps if the SDK allows.
    *   *Likely files to edit: `orchestrator.py`, potentially `csv_mcp/agents.py` (for `PrimaryInteractionAgent` instructions/output)*
*   **Streaming Output**:
    *   Implement streaming for agent responses (especially for longer text like analysis summaries) to make the application feel more responsive. Refer to OpenAI Agents SDK documentation on Streaming.
    *   *Likely files to edit: `orchestrator.py` (to handle streaming from `Runner.run`), potentially `csv_mcp/agents.py` (if agent configuration needs to enable/support streaming explicitly)*
*   **Better Output Formatting**:
    *   Format complex outputs (detailed Q&A, multi-part analysis) more clearly in the console.
    *   *Likely files to edit: `orchestrator.py` (in the section where `assistant_response` is processed and printed)*
*   **Persistent History (Optional)**:
    *   Consider saving conversation history and `session_reports` to a file to allow sessions to be resumed.
    *   *Likely files to edit: `orchestrator.py` (to add load/save logic)*
*   **Contextual Help**:
    *   Enhance `PrimaryInteractionAgent` to offer detailed help on its capabilities, the roles of specialized agents, and example commands.
    *   *Likely files to edit: `csv_mcp/agents.py` (instructions for `build_primary_interaction_agent`)*

## 3. Advanced Agent Capabilities & Orchestration (Towards Phase B of original plan)

*   **Multi-Step Tasks (Coordinator Logic for `PrimaryInteractionAgent`)**:
    *   Enable `PrimaryInteractionAgent` to decompose complex user requests into a sequence of handoffs (e.g., "Analyze, then transform, then answer Q&A").
    *   Manage the data flow and context between chained handoffs.
    *   *Likely files to edit: `csv_mcp/agents.py` (major changes to `PrimaryInteractionAgent` instructions, possibly its Pydantic input/output models if it needs to manage state for sequences), `orchestrator.py` (to potentially support more complex state passing or loop control based on `PrimaryInteractionAgent`'s plan)*
*   **Tool Usage by Specialized Agents**:
    *   Equip specialized agents with their own tools for tasks beyond LLM capabilities (e.g., specific statistical calculations, external data lookups). This would involve defining new tool functions and adding them to the respective agent configurations.
    *   *Likely files to edit: `csv_mcp/agents.py` (to add tool definitions and associate them with agents), potentially new Python files for complex tool logic.*
*   **Dynamic Agent Configuration/Selection**:
    *   For highly advanced scenarios, explore dynamic configuration or selection/building of agents based on initial data or user goals.
    *   *Likely files to edit: `orchestrator.py` (major architectural changes), `csv_mcp/agents.py` (to support more flexible agent building)*
*   **Context Management (`RunContextWrapper`)**:
    *   Utilize the SDK's `context` object in `Runner.run()` for more structured state management (shared state, DB connections, user-specific info) accessible by all agents and tools. Refer to SDK documentation on Context.
    *   *Likely files to edit: `orchestrator.py` (to define and pass the context object), `csv_mcp/agents.py` (if agents or their Pydantic models need to be aware of or use the context type).*

## 4. Refined Prompts and Pydantic Models

*   **Iterative Prompt Engineering**:
    *   Continuously test and refine instructions for all agents to improve accuracy, handoff reliability, and output quality.
    *   *Likely files to edit: `csv_mcp/agents.py` (instructions for all agent builders)*
*   **More Specific Pydantic Output Models**:
    *   Make `AnalysisOutput` and `QnAOutput` more granular with specific fields (e.g., `key_findings: list[str]`, `data_summary_statistics: dict` for analysis) to guide LLM output and improve programmatic usability.
    *   *Likely files to edit: `csv_mcp/agents.py` (definitions of `AnalysisOutput`, `QnAOutput`, and corresponding agent instructions)*

## 5. Testing

*   **Comprehensive Test Suite**:
    *   Develop a suite of test cases covering various user queries (simple, complex, ambiguous, different handoffs, transformations, session summaries) to ensure robust and expected behavior.
    *   *Likely files to edit: This would likely involve creating new test files (e.g., in a `tests/` directory using a framework like `pytest`). While not editing the core application files directly for this point, it's a crucial part of development.* 