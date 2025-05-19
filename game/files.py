"""File management

Contributors:
    Romain
"""

from __future__ import annotations
import logging
import os
import pickle

logger = logging.getLogger(__name__)


def load_text(path: str) -> str:
    """
    Reads and returns the content of the text file at the provided path.
    """
    logger.debug(f"Loading text file: {path}")

    try:
        with open(path, "r", encoding="utf-8") as file:
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
    logger.debug(f"Loading text file directory: {path}")

    texts = {}
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)
        name, ext = os.path.splitext(entry)

        if ext != ".txt":
            logger.warning(f"Expected text file at path: {full_path}")
            continue

        texts[name] = load_text(full_path)

    return texts


def save_pickle(obj: object, path: str) -> None:
    """
    Saves an object as a pickle file at the provided path.
    """
    logger.debug(f"Saving pickle file: {path}")
    with open(path, "wb") as file:
        pickle.dump(obj, file)


def load_pickle(path: str) -> object:
    """
    Reads and returns the pickle object at the provided path.
    """
    logger.debug(f"Loading pickle file: {path}")
    try:
        with open(path, "rb") as file:
            return pickle.load(file)

    except FileNotFoundError:
        error_msg = f"File missing: {path}"
        logger.error(error_msg)
        return None


def delete(file_path: str) -> None:
    """
    Deletes the file at file_path.
    """
    os.remove(file_path)


def _test():
    """Execute a series of test to see if the program is working"""
    file_1 = "10"
    save_pickle(file_1, "test")
    assert load_pickle("test") == "10"
    with open("test", "w", encoding="utf-8") as file:
        file.write(file_1)
    assert load_text("test") == "10"
    delete("test")
    assert "test" not in os.listdir()
    print("all Tests passed")


if __name__ == "__main__":
    _test()
