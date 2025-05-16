"""File management

Contributors:
    Romain
"""

from __future__ import annotations
import logging
import os
import pickle
from typing import NamedTuple
from game_classes import Character, Stats
from enums import EVENT_TYPES

class Save(NamedTuple):
    """Un fichier de sauvgarde"""
    character : Character
    worldPosition : tuple[str, int, int] #le premier int représente l'axe y et le deuxième l'axe x
    
    @classmethod
    def new(cls,
            character: Character = Character.new(
                "Hero",
                "assets\\sprites\\characters\\player",
                True,
                #        MHP, MST, MMA, STR, AGI, ACU, ARM, RES
                Stats(8, 16, 4, 8, 6, 4, 2, 4),
                [],
                {}
            ),
            worldPosition: tuple[str, int, int] = ("test_zone.pkl", 3, 3)
           ) -> Save:
        """Create a new Savefile"""
        logger.debug(f"the save {Save(character, worldPosition)} is created ")
        return Save(character, worldPosition)
    
        
    #def _test():
    #    save1 = Save.new(worldPosition=("zone2.pkl", 5, 5))
    #    save2 = Save.new(worldPosition=("zone1.pkl", 3, 7))
    #    Save.save(None, save1,"save_1")
    #    save2 = Save.load("save_1", "save_1")
    #    assert save2 == save1
    #    delete("save_1.pkl", "Saves\\Game_Saves")
    #    print("Save tests passed")


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

if __name__ == "__main__":
    Save._test()