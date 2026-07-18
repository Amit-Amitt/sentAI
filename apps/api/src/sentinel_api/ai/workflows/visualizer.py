from typing import Any, Dict, List
from sentinel_api.ai.workflows.graph import get_compiled_graph


class WorkflowVisualizer:
    """Helper to visualize the Sentinel AI LangGraph workflow structure.

    Generates Mermaid syntax and serializable metadata.
    """

    def __init__(self) -> None:
        self.graph = get_compiled_graph()

    def generate_mermaid(self) -> str:
        """Returns the Mermaid diagram representation of the workflow graph."""
        # Use LangGraph's built-in get_graph().draw_mermaid() method
        return self.graph.get_graph().draw_mermaid()

    def get_visualization_metadata(self) -> Dict[str, Any]:
        """Generates JSON-serializable node and edge metadata for frontend rendering."""
        raw_graph = self.graph.get_graph()

        nodes: List[Dict[str, str]] = []
        # Exclude internal/virtual nodes like __start__ and __end__ if desired,
        # or include them labeled clearly.
        for node_id in raw_graph.nodes.keys():
            label = node_id.replace("_", " ").title()
            if node_id == "__start__":
                label = "Start"
            elif node_id == "__end__":
                label = "End"
            nodes.append({"id": node_id, "label": label})

        links: List[Dict[str, str]] = []
        for edge in raw_graph.edges:
            # Handle edge object attributes safely
            source = getattr(edge, "source", "")
            target = getattr(edge, "target", "")
            data = getattr(edge, "data", None)

            # Check if conditional edge
            is_conditional = (
                "conditional" in str(type(edge)).lower()
                or data is not None
            )

            links.append(
                {
                    "source": source,
                    "target": target,
                    "conditional": "true" if is_conditional else "false",
                }
            )

        return {"nodes": nodes, "edges": links}
