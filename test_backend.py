import os
import pytest
from autodoc_swarm.backend import SecureFilesystemBackend
from autodoc_swarm.tools import check_file_freshness

def test_secure_backend(tmp_path):
    backend = SecureFilesystemBackend(root_dir=str(tmp_path))

    env_file = tmp_path / ".env"
    env_file.write_text("SECRET=123")

    with pytest.raises(PermissionError):
        backend.read(".env")

    with pytest.raises(PermissionError):
        backend.write(".env", "HACK")

def test_freshness(tmp_path):
    source_file = tmp_path / "source.py"
    doc_file = tmp_path / "doc.md"

    source_file.write_text("a")

    import time
    time.sleep(0.1)

    doc_file.write_text("b")

    assert not check_file_freshness(str(source_file), str(doc_file))

    time.sleep(0.1)
    source_file.write_text("c")

    assert check_file_freshness(str(source_file), str(doc_file))
