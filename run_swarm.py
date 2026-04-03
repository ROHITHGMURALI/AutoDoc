import typer
import os
from typing import Optional
from dotenv import load_dotenv

from autodoc_swarm.agent import create_swarm

app = typer.Typer(help="AutoDoc Agent Swarm CLI")

@app.command()
def run(
    target: str = typer.Option(".", help="Target repository path"),
    force_update: bool = typer.Option(False, help="Force update all documentation, ignoring freshness checks"),
    provider: str = typer.Option("openrouter", help="LLM Provider (openrouter, anthropic, openai, google)"),
    queen_model: str = typer.Option("anthropic/claude-3.5-sonnet", help="Model name for the Swarm Queen"),
    worker_model: str = typer.Option("anthropic/claude-3.5-sonnet", help="Model name for the Swarm Worker"),
    drone_model: str = typer.Option("anthropic/claude-3.5-sonnet", help="Model name for the Swarm Drone")
):
    """
    Run the AutoDoc Agent Swarm to generate documentation for a repository.
    """
    load_dotenv()
    typer.echo(f"Starting Swarm on {target} using provider: {provider}")
    typer.echo(f"Queen Model: {queen_model} | Worker Model: {worker_model} | Drone Model: {drone_model}")

    if force_update:
        typer.echo("Warning: --force-update flag provided. Note: This feature is simulated as true via Queen prompt adjustments in future scopes. Standard run proceeding.")

    try:
        queen = create_swarm(
            target_dir=target,
            provider=provider,
            queen_model=queen_model,
            worker_model=worker_model,
            drone_model=drone_model
        )

        typer.echo("Executing deep scan and documentation planning...")
        # Start the run
        # Note: We provide a kick-off message to start the autonomous loop
        response = queen.invoke({"messages": [("user", "Begin a deep scan of the repository. Evaluate freshness of files and document all code files found according to your directives. Stop when all tasks are complete.")]})

        final_output = response["messages"][-1].content if "messages" in response and response["messages"] else str(response)

        typer.echo("\n--- Final Queen Output ---")
        typer.echo(final_output)
        typer.echo("--------------------------")

    except Exception as e:
        typer.secho(f"Error executing swarm: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
