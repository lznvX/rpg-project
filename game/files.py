"""File management

Contributors:
    Romain
"""

from __future__ import annotations
import logging
import os
import pickle
from typing import NamedTuple
from enums import EVENT_TYPES


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


def save_pickle(obj: object, path: str) -> None:
    """Saves an object as a pickle file at the provided path."""
    with open(path, "wb") as file:
        logger.debug(f"Saved pickle file: {path}")
        pickle.dump(obj, file)


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


def delete(file : str, filepath : str):
    liste_file = os.listdir(filepath)
    if file in liste_file:
        os.remove(filepath+"\\"+file)
    else:
        print(f"Le fichier {file} n'est pas dans le bon dossier.") 


logger = logging.getLogger(__name__)
