"""File management

Contributors:
    Romain
"""

import logging
import os
import pickle


def load_text(path: str) -> str:
    """Reads and returns the content of the text file at the provided path."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            logger.debug(f"Loaded text file: {path}")
            return file.read()

    except FileNotFoundError:
        error_msg = f"File missing: {path}"
        logger.error(error_msg)
        return error_msg


def load_text_dir(path: str) -> dict[str, str]:
    """
    Returns a dict with keys being the filenames, values being the contents of
    the files in the directory.
    """
    texts = {}

    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        name, ext = os.path.splitext(entry)

        if ext != ".txt":
            logger.warning(f"Expected text file at path: {full_path}")
            continue

        texts[name] = load_text(full_path)
    
    logger.debug(f"Loaded text file directory: {path}")
    return texts


def load_pickle(path: str) -> object:
    """Reads and returns the pickle object at the provided path."""
    try:
        with open(path, "rb") as file:
            logger.debug(f"Loaded pickle file: {path}")
            return pickle.load(file)

    except FileNotFoundError:
        error_msg = f"File missing: {path}"
        logger.error(error_msg)
        return None


logger = logging.getLogger(__name__)
