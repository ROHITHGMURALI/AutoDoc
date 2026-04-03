import os

def check_file_freshness(source_path: str, doc_path: str) -> bool:
    """
    Checks if the source file is newer than the documentation file.
    Returns True if the source file is newer (or doc doesn't exist), meaning docs need to be updated.
    """
    try:
        if not os.path.exists(doc_path):
            return True
        source_mtime = os.path.getmtime(source_path)
        doc_mtime = os.path.getmtime(doc_path)
        return source_mtime > doc_mtime
    except FileNotFoundError:
        # If source doesn't exist, we don't need to document it (maybe it was deleted)
        return False
