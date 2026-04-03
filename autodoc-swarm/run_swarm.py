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
    model: str = typer.Option("anthropic/claude-3.5-sonnet", help="Model name (e.g., anthropic/claude-3.5-sonnet, gpt-4o)")
):
    """
    Run the AutoDoc Agent Swarm to generate documentation for a repository.
    """
    load_dotenv()
    typer.echo(f"Starting Swarm Queen on {target} using {provider}:{model}")

    if force_update:
        typer.echo("Warning: --force-update flag provided. Note: This feature is simulated as true via Queen prompt adjustments in future scopes. Standard run proceeding.")

    try:
        queen = create_swarm(target_dir=target, provider=provider, model=model)

        typer.echo("Executing deep scan and documentation planning...")
        # Start the run
        # Note: We provide a kick-off message to start the autonomous loop
        response = queen.run("Begin a deep scan of the repository. Evaluate freshness of files and document all code files found according to your directives. Stop when all tasks are complete.")

        typer.echo("\n--- Final Queen Output ---")
        typer.echo(response)
        typer.echo("--------------------------")

    except Exception as e:
        typer.secho(f"Error executing swarm: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
