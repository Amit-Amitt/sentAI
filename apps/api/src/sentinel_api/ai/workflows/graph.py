from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph.state import CompiledStateGraph
from sentinel_api.ai.workflows.builder import create_workflow_graph


def get_compiled_graph() -> CompiledStateGraph:
    """Compiles the Sentinel AI workflow graph with an in-memory checkpointer

    to support state persistence, step execution, pause, and resume.
    """
    builder = create_workflow_graph()
    checkpointer = MemorySaver()
    return builder.compile(checkpointer=checkpointer)
