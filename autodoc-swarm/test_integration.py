import pytest
from unittest.mock import patch, MagicMock

@patch('autodoc_swarm.agent.get_llm')
@patch('autodoc_swarm.agent.create_deep_agent')
@patch('autodoc_swarm.agent.SubAgent')
def test_swarm_initialization(mock_subagent, mock_create_deep_agent, mock_get_llm):
    from autodoc_swarm.agent import create_swarm

    mock_llm = MagicMock()
    mock_get_llm.return_value = mock_llm

    # Just testing we can create the swarm and access tools without issues
    queen = create_swarm(target_dir="./dummy_repo", provider="openai", model="gpt-4o")

    mock_get_llm.assert_called_with("openai", "gpt-4o")
    mock_create_deep_agent.assert_called_once()
    assert mock_subagent.call_count == 2

def test_check_file_freshness_logic():
    from autodoc_swarm.tools import check_file_freshness
    import os
    import time

    with open("test_src.py", "w") as f: f.write("src")

    # Doc doesn't exist -> should be true
    assert check_file_freshness("test_src.py", "test_doc.md") == True

    # Doc is newer -> should be false
    time.sleep(0.1)
    with open("test_doc.md", "w") as f: f.write("doc")
    assert check_file_freshness("test_src.py", "test_doc.md") == False

    # Source is newer -> should be true
    time.sleep(0.1)
    with open("test_src.py", "w") as f: f.write("src2")
    assert check_file_freshness("test_src.py", "test_doc.md") == True

    os.remove("test_src.py")
    os.remove("test_doc.md")

def test_mirrored_directory_structure(tmp_path):
    # This test verifies that if the swarm agent writes a doc file,
    # it can successfully create a mirrored directory structure.
    # While we mocked the LLM in `test_swarm_initialization`,
    # here we can manually test the backend behavior that the worker uses
    # to write documentation.

    from autodoc_swarm.backend import SecureFilesystemBackend
    import os

    # root_dir is our temporary path
    backend = SecureFilesystemBackend(root_dir=str(tmp_path))

    # Emulate the worker writing a file deep in a mirrored directory
    # DeepAgents backend.write creates intermediate directories
    doc_path = "documentation/src/api/routes.md"
    content = "# Routes\n"

    backend.write(doc_path, content)

    # Verify the file was created and content matches
    full_path = tmp_path / "documentation" / "src" / "api" / "routes.md"
    assert full_path.exists()
    assert full_path.read_text() == content
