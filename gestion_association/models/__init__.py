from enum import Enum


class OuiNonChoice(Enum):
    OUI = "Oui"
    NON = "Non"


class TypeChoice(Enum):
    CHAT = "Chat"
    CHIEN = "Chien"


class PerimetreChoice(Enum):
    UN = "Périmètre 1 (Marjo)"
    DEUX = "Périmètre 2 (Lucile)"