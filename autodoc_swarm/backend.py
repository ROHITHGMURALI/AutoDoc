import os
import re
from pathlib import Path
from typing import List, Union, Any

from deepagents.backends import FilesystemBackend

class SecureFilesystemBackend(FilesystemBackend):
    def __init__(self, root_dir: str = ".", virtual_mode: bool = False, *args, **kwargs):
        super().__init__(root_dir=root_dir, virtual_mode=virtual_mode, *args, **kwargs)
        self._root_dir = root_dir
        self.blocked_patterns = [
            re.compile(r'\.env.*'),
            re.compile(r'.*\.pem$'),
            re.compile(r'.*credentials.*', re.IGNORECASE),
            re.compile(r'.*secret.*', re.IGNORECASE),
            re.compile(r'.*ignore$', re.IGNORECASE),  # .gitignore, .dockerignore, .npmignore, etc.
        ]
        self.blocked_dirs = {
            ".git",
            "node_modules",
            "venv",
            ".venv",
            "__pycache__"
        }

    def _normalize_path(self, path_str: str) -> str:
        """
        LLMs sometimes pass paths with a leading slash, full workspace prefix,
        or redundant root_dir prefix. Normalize to a plain relative path.
        e.g. "/dummy_repo/src/api.py"              -> "src/api.py"
             "github/workspace/dummy_repo/src/api.py" -> "src/api.py"
        """
        path = Path(path_str)

        # Strip leading slash to convert absolute -> relative
        if path.is_absolute():
            path = Path(*path.parts[1:])

        # Find root_dir parts (strip leading './' if present)
        root_parts = tuple(p for p in Path(self._root_dir).parts if p != ".")

        # Search for root_dir parts anywhere in the path and strip everything up to and including them
        if root_parts:
            parts = path.parts
            for i in range(len(parts)):
                if parts[i:i + len(root_parts)] == root_parts:
                    remaining = parts[i + len(root_parts):]
                    path = Path(*remaining) if remaining else Path(".")
                    break

        return str(path)

    def _is_allowed(self, path_str: str) -> bool:
        path = Path(path_str)

        # Reject absolute paths — they escape root_dir confinement
        # (os.path.join(root, "/abs") returns "/abs", discarding root)
        if path.is_absolute():
            return False

        # Reject path traversal attempts
        if ".." in path.parts:
            return False

        # Check if any part of the path is a blocked directory
        for part in path.parts:
            if part in self.blocked_dirs:
                return False

        # Check if filename matches blocked patterns
        filename = path.name
        for pattern in self.blocked_patterns:
            if pattern.search(filename):
                return False

        return True

    def read(self, path: str, *args, **kwargs) -> str:
        path = self._normalize_path(path)
        if not self._is_allowed(path):
            raise PermissionError(f"Access to {path} is denied for security reasons.")
        return super().read(path, *args, **kwargs)

    def write(self, path: str, content: str) -> Any:
        path = self._normalize_path(path)
        if not self._is_allowed(path):
            raise PermissionError(f"Access to {path} is denied for security reasons.")
        return super().write(path, content)

    def ls_info(self, path: str = ".") -> list[dict]:
        path = self._normalize_path(path)
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
        except FileNotFoundError:
            return []
        except Exception as e:
            print(f"Error reading directory: {e}")
            raise
