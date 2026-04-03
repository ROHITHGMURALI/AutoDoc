FROM python:3.12-slim

# Install git and other essential tools
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
ENV UV_INSTALL_DIR="/usr/local/bin"
RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR="/usr/local/bin" bash

# Set the working directory
WORKDIR /app

# Copy the dependency files first for caching
COPY pyproject.toml .

# Install dependencies using uv into the system python environment
RUN uv pip install --system deepagents langchain-openai langchain-anthropic langchain-google-genai pydantic tenacity typer python-dotenv

# Copy the rest of the application
COPY autodoc_swarm /app/autodoc_swarm
COPY entrypoint.py /app/entrypoint.py

# Ensure git trusts the workspace
RUN git config --global --add safe.directory /github/workspace

ENTRYPOINT ["python", "/app/entrypoint.py"]
