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

    # Actions
    # attacks
    light_stab_name: str
    light_stab_desc: str

    stab_name: str
    stab_desc: str

    slash_name: str
    slash_desc: str


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

    # Actions
    # attacks
    light_stab_name = "Light Stab",
    light_stab_desc = "Stab your opponent with your puny dagger",

    stab_name   = "Stab",
    stab_desc   = "Stick 'em with the pointy end",

    slash_name  = "Slash",
    slash_desc  = "Swing your sword at your opponent",
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

    # Actions
    # attacks
    light_stab_name = "Coup de couteau",
    light_stab_desc = "Poignardez votre ennemi avec votre petit couteau",

    stab_name   = "Coup de poignard",
    stab_desc   = "Frappez de l'estoc",

    slash_name  = "Coup d'épée",
    slash_desc  = "Brandissez votre épée sur votre ennemi",
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
