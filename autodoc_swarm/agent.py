import os
from typing import Optional
from deepagents import create_deep_agent, SubAgent
from .prompts import QUEEN_SYSTEM_PROMPT, WORKER_SYSTEM_PROMPT, DRONE_SYSTEM_PROMPT
from .backend import SecureFilesystemBackend
from .tools import check_file_freshness
from .llm_setup import get_llm

def create_swarm(target_dir: str, provider: str, queen_model: str, worker_model: str, drone_model: str):
    llm_queen = get_llm(provider, queen_model)
    llm_worker = get_llm(provider, worker_model)
    llm_drone = get_llm(provider, drone_model)

    backend = SecureFilesystemBackend(root_dir=target_dir)

    worker_desc = "Technical Writer subagent that reads source code and generates documentation."
    worker = SubAgent(
        name="worker",
        description=worker_desc,
        system_prompt=WORKER_SYSTEM_PROMPT,
        model=llm_worker,
    )

    drone_desc = "Devil's Advocate / QA subagent that critiques documentation and validates requirements."
    drone = SubAgent(
        name="drone",
        description=drone_desc,
        system_prompt=DRONE_SYSTEM_PROMPT,
        model=llm_drone,
    )

    queen = create_deep_agent(
        system_prompt=QUEEN_SYSTEM_PROMPT,
        model=llm_queen,
        backend=backend,
        subagents=[worker, drone],
        tools=[check_file_freshness]
    )

    return queen
