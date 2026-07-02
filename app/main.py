from __future__ import annotations

from rich.console import Console
from rich.table import Table

from app.graph.state import GraphState
from app.graph.workflow import finalize_session, initialize_daily_plan, run_next_robot_turn
from app.nodes.progress_checker import check_progress
from app.utils.config import get_settings
from app.utils.logging import save_session_log

console = Console()


def print_plan(state: GraphState) -> None:
    table = Table(title="Daily HRCare-GR Plan")
    table.add_column("Time")
    table.add_column("Activity")
    table.add_column("Category")
    table.add_column("Priority")
    table.add_column("Critical")

    for a in state.activities:
        table.add_row(a.preferred_time, a.title, a.category, str(a.priority), "yes" if a.safety_critical else "no")
    console.print(table)


def main() -> None:
    settings = get_settings()
    console.print("[bold]HRCare-GR Assistive Robot Simulation[/bold]")
    patient_id = input("Patient ID (P001/P002): ").strip() or "P001"
    doctor_instructions = input("Doctor instructions for today (optional): ").strip()
    simulation_time = input("Simulation start time HH:MM (default 08:00): ").strip() or "08:00"

    state = GraphState(
        patient_id=patient_id,
        doctor_instructions=doctor_instructions,
        simulation_time=simulation_time,
    )
    state = initialize_daily_plan(state)

    console.print(f"\nLoaded patient: [bold]{state.patient.name if state.patient else patient_id}[/bold]")
    if state.memory_notes:
        console.print("\n[blue]Memory context[/blue]")
        for note in state.memory_notes:
            console.print(f"- {note}")

    print_plan(state)

    if state.warnings:
        console.print("\n[yellow]Warnings[/yellow]")
        for warning in state.warnings:
            console.print(f"- {warning}")

    while True:
        state = run_next_robot_turn(state)
        if state.current_activity_id is None:
            break

        robot_message = state.conversation[-1].text
        console.print(f"\n[cyan]Robot:[/cyan] {robot_message}")
        reply = input("Patient reply: ").strip()
        state = check_progress(state, reply)

    state = finalize_session(state)
    log_path = save_session_log(state, settings.log_dir)
    console.print(f"\n[green]Session completed.[/green] Log saved at: {log_path}")


if __name__ == "__main__":
    main()
