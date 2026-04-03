import os
import re
from pathlib import Path
from typing import List, Union, Any

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

    def write(self, path: str, content: str) -> Any:
        if not self._is_allowed(path):
            raise PermissionError(f"Access to {path} is denied for security reasons.")
        return super().write(path, content)

    def ls_info(self, path: str = ".") -> List[dict]:
        try:
            result = super().ls_info(path)
            allowed_items = []
            for item in result:
                item_path = item.get("path", "")

                # Check if any part of the path is a blocked directory
                path_parts = Path(item_path).parts
                blocked = False
                for part in path_parts:
                    if part in self.blocked_dirs:
                        blocked = True
                        break

                if blocked:
                    continue

                # Check if filename matches blocked patterns
                filename = Path(item_path).name
                for pattern in self.blocked_patterns:
                    if pattern.search(filename):
                        blocked = True
                        break

                if not blocked:
                    allowed_items.append(item)
            return allowed_items
        except Exception as e:
            # We return empty list on error to match the return type expected
            print(f"Error reading directory: {e}")
            return []
