import os
import re
from pathlib import Path
from typing import List, Union

from deepagents.backends import FilesystemBackend

class SecureFilesystemBackend(FilesystemBackend):
    def __init__(self, root_dir: str = ".", virtual_mode: bool = False, *args, **kwargs):
        super().__init__(root_dir=root_dir, virtual_mode=virtual_mode, *args, **kwargs)
        self.blocked_patterns = [
            re.compile(r'\.env.*'),
            re.compile(r'.*\.pem$'),
            re.compile(r'.*credentials.*', re.IGNORECASE),
            re.compile(r'.*secret.*', re.IGNORECASE),
        ]
        self.blocked_dirs = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__"
        }

    def _is_allowed(self, path_str: str) -> bool:
        path = Path(path_str)
        # Check if any part of the path is a blocked directory
        for part in path.parts:
            if part in self.blocked_dirs:
                return False

        # Check if filename matches blocked patterns
        filename = path.name
        for pattern in self.blocked_patterns:
            if pattern.match(filename):
                return False

        return True

    def read(self, path: str, *args, **kwargs) -> str:
        if not self._is_allowed(path):
            raise PermissionError(f"Access to {path} is denied for security reasons.")
        return super().read(path, *args, **kwargs)

    def write(self, path: str, content: str) -> None:
        if not self._is_allowed(path):
            raise PermissionError(f"Access to {path} is denied for security reasons.")
        super().write(path, content)

    def ls_info(self, path: str = ".") -> str:
        # Note: Depending on deepagents implementation we might need to filter the output of ls_info
        # Instead, we'll try to intercept what we can or rely on standard ls output filtering
        try:
            result = super().ls_info(path)
            # Basic naive filtering of ls output
            lines = result.splitlines()
            allowed_lines = []
            for line in lines:
                # Naive check if any blocked word is in the line.
                # A more robust approach depends on the exact output format of ls_info.
                blocked = False
                for b_dir in self.blocked_dirs:
                    if b_dir in line:
                        blocked = True
                        break
                if not blocked:
                    for pattern in self.blocked_patterns:
                        if pattern.search(line):
                            blocked = True
                            break
                if not blocked:
                    allowed_lines.append(line)
            return "\n".join(allowed_lines)
        except Exception as e:
            return f"Error reading directory: {e}"
