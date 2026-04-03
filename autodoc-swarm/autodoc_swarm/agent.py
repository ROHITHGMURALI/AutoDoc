import os
from typing import Optional
from deepagents import create_deep_agent, SubAgent
from .prompts import QUEEN_SYSTEM_PROMPT, WORKER_SYSTEM_PROMPT, DRONE_SYSTEM_PROMPT
from .backend import SecureFilesystemBackend
from .tools import check_file_freshness
from .llm_setup import get_llm

def create_swarm(target_dir: str, provider: str, model: str):
    llm_model = get_llm(provider, model)
    backend = SecureFilesystemBackend(root_dir=target_dir)

    worker = SubAgent(
        name="worker",
        role="Technical Writer subagent that reads source code and generates documentation.",
        system_prompt=WORKER_SYSTEM_PROMPT,
        model=llm_model,
        backend=backend
    )

    drone = SubAgent(
        name="drone",
        role="Devil's Advocate / QA subagent that critiques documentation and validates requirements.",
        system_prompt=DRONE_SYSTEM_PROMPT,
        model=llm_model,
        backend=backend
    )

    queen = create_deep_agent(
        system_prompt=QUEEN_SYSTEM_PROMPT,
        model=llm_model,
        backend=backend,
        subagents=[worker, drone],
        tools=[check_file_freshness]
    )

    return queen
