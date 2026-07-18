import asyncio
import sys
import os

# Add src to python path
sys.path.insert(0, os.path.abspath("src"))

from sentinel_api.ai.schemas.models import ExecutionContext, IncidentContext
from sentinel_api.ai.workflows import WorkflowExecutor, WorkflowVisualizer


def print_title(title: str):
    print("\n" + "=" * 80)
    print(f" {title.upper()} ".center(80, "="))
    print("=" * 80)


def print_state_info(result: dict):
    print(f"Thread ID:  {result.get('thread_id')}")
    print(f"Status:     {result.get('status')}")
    print(f"Duration:   {result.get('duration_ms', 0):.2f} ms")
    if "state" in result and result["state"]:
        state = result["state"]
        print(f"Visited Nodes: {state.get('visited_nodes')}")
        print(f"Retry Count:   {state.get('retry_count')}")
        print(f"Errors Count:  {len(state.get('errors', []))}")
        print("Timeline:")
        for idx, event in enumerate(state.get("execution_timeline", [])):
            duration = event.get("duration_ms", 0)
            status = event.get("status", "unknown")
            err_msg = f" (Error: {event['error']})" if "error" in event else ""
            print(
                f"  {idx+1}. [{event['node']}] -> {status}{err_msg} ({duration:.2f} ms)"
            )


async def main():
    incident = IncidentContext(
        incident_id="inc-999",
        severity="SEV1",
        status="active",
        summary="Database connection pool exhaustion in prod-db-01",
    )
    execution = ExecutionContext(
        request_id="req-999",
        correlation_id="corr-999",
        agent_id="sentinel-orchestrator",
    )

    executor = WorkflowExecutor()
    visualizer = WorkflowVisualizer()

    # --- 1. Mermaid Graph ---
    print_title("1. Mermaid Diagram Generation")
    print(visualizer.generate_mermaid())

    # --- 2. Sequential Execution ---
    print_title("2. Default Sequential Workflow Execution")
    res_seq = await executor.start(incident, execution)
    print_state_info(res_seq)

    # --- 3. Parallel Execution ---
    print_title("3. Parallel Workflow Execution (Log & Metrics Concurrent)")
    res_para = await executor.start(
        incident, execution, intermediate_results={"parallel": True}
    )
    print_state_info(res_para)

    # --- 4. Conditional Branching ---
    print_title("4. Conditional Branching (Skip Metrics & Review)")
    res_cond = await executor.start(
        incident,
        execution,
        intermediate_results={"branch": "skip_metrics"},
    )
    print_state_info(res_cond)

    # --- 5. Failure & Automatic Retry ---
    print_title("5. Node Failure & Automatic Retry (Coordinator Fails twice)")
    res_retry = await executor.start(
        incident,
        execution,
        intermediate_results={
            "fail_node": "coordinator",
            "fail_node_max_retries": 2,
            "max_retries": 2,
        },
    )
    print_state_info(res_retry)

    # --- 6. Manual Retry Node ---
    print_title("6. Node Failure & Manual Node Resume / Retry")
    # Simulate a coordinator failure that exceeds retries
    res_fail = await executor.start(
        incident,
        execution,
        intermediate_results={
            "fail_node": "coordinator",
            "fail_node_max_retries": 3,
            "max_retries": 1,
        },
    )
    print("Initial Run Result (Should exceed retries):")
    print_state_info(res_fail)

    thread_id = res_fail["thread_id"]
    print("\n--- Triggering Manual Retry of coordinator node ---")
    res_manual = await executor.retry_node(thread_id, "coordinator")
    print_state_info(res_manual)


if __name__ == "__main__":
    asyncio.run(main())
