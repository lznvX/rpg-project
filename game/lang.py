"""Language management

Created on 2025.03.17
Contributors:
    Jakub
"""


from typing import NamedTuple


class _Lang(NamedTuple):

    # Combat
    battle_begin: str
    battle_win: str
    battle_loss: str
    battle_rewards: str
    battle_turn: str

    battle_attack: str
    battle_damage: str
    battle_death: str
    battle_ko: str
    battle_action_choice: str
    battle_target_choice: str

    # Items
    item_names: dict[str, str]
    # item_names = {
    #     "item_name": "Item Name"
    # }
    item_descriptions: dict[str, str]
    # item_descriptions = {
    #     "item_name": "Item Description"
    # }

    # Actions
    action_names: dict[str, str]
    # action_names = {
    #     "action_name": "Action Name"
    # }
    action_descriptions: dict[str, str]
    # action_descriptions = {
    #     "action_name": "Action Description"
    # }


English = _Lang(

    # Combat
    battle_begin    = "You are now in battle!",
    battle_win      = "You won the battle!",
    battle_loss     = "You lost the battle :(",
    battle_rewards  = "You gain {} gold and {} xp!",
    battle_turn     = "Turn {} begins!",

    battle_attack   = "{} uses {} on {}",
    battle_damage   = "{} takes ¤ {} damage! (♥ {} left)",
    battle_death    = "{} dies!",
    battle_ko       = "{} is knocked out!",
    battle_action_choice    = "What should {} do?",
    battle_target_choice    = "Choose target for {}:",

    # Items
    item_names = {
      # "item_name": "Item Name",
        "agi_boots": "Hermes' Boots",
        "potion_health": "Potion of Healing",
        "str_helmet": "Helmet of Strength",
        "sword": "Sword",
    },
    item_descriptions = {
    #   "item_name": "Item Description",
        "agi_boots": "A pair of boots with suspicious wings",
        "potion_health": "Heals ♥ 5 when consumed",
        "str_helmet": "A spartan helmet, enchanted with a strength spell",
        "sword": "A pointy thing",
    },

    # Actions
    action_names = {
      # "action_name": "Action Name",
        "light_stab": "Light Stab",
        "slash": "Slash",
        "stab": "Stab",
    },
    action_descriptions = {
      # "action_name": "Action Description",
        "light_stab": "Stab your opponent with your puny dagger",
        "slash": "Swing your sword at your opponent",
        "stab": "Stick 'em with the pointy end",
    },
    )


French = _Lang(

    # Combat
    battle_begin    = "Vous êtes maintenant en combat !",
    battle_win      = "Vous avez gagné le combat !",
    battle_loss     = "Vous avez perdu le combat :(",
    battle_rewards  = "Vous gagnez {} pièces d'or et {} xp !",
    battle_turn     = "Le tour {} commence !",

    battle_attack   = "{} utilise {} sur {}",
    battle_damage   = "{} prend ¤ {} dégats ! (il reste ♥ {})",
    battle_death    = "{} meurt !",
    battle_ko       = "{} est assommé !",
    battle_action_choice    = "Que'est-ce que {} devrait faire ?",
    battle_target_choice    = "Choisissez la cible de {}:",


    # Items
    item_names = {
      # "item_name": "Item Name",
        "agi_boots": "Bottes de Hermes",
        "potion_health": "Potion de Gueérisson",
        "str_helmet": "Heaume de Force",
        "sword": "Épée",
    },
    item_descriptions = {
    #   "item_name": "Item Description",
        "agi_boots": "Une pair de bottes avec des ailes suspicieuses",
        "potion_health": "Guérit ♥ 5 lors de consommation",
        "str_helmet": "Une heaume spartane, enchantée avec un sort de force",
        "sword": "Un truc pointu",
    },

    # Actions
    action_names = {
      # "action_name": "Action Name",
        "light_stab": "Coup de couteau",
        "slash": "Coup d'épée",
        "stab": "Coup de pointe",
    },
    action_descriptions = {
      # "action_name": "Action Description",
        "light_stab": "Poignardez votre ennemi avec votre arme",
        "slash": "Brandissez votre épée sur votre ennemi",
        "stab": "Frappez l'enemi avec la pointe de votre arme",
    },
    )


def get_lang_choice() -> _Lang:
    """Returns the class with text in the relevant language.

    Language is specified in options.txt (not implemented)
    If language is not specified, or options.txt file is missing, English is
    used by default.
    """
    return English


def f(fstring: str, *args: object) -> str:
    """Shorthand for fstring.format(*args)."""
    return fstring.format(*args)
