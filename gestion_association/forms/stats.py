from enum import Enum
from django.forms import ChoiceField, Form, Select
from django.db.models import BLANK_CHOICE_DASH

class AnneeChoice(Enum):
    ANNEE_2020 = "2020"
    ANNEE_2021 = "2021"
    ANNEE_2022 = "2022"
    ANNEE_2023 = "2023"
    ANNEE_2024 = "2024"
    ANNEE_2025 = "2025"
    ANNEE_2026 = "2026"
    ANNEE_2027 = "2027"
    ANNEE_2028 = "2028"
    ANNEE_2029 = "2029"
    ANNEE_2030 = "2030" 


class AgeChoice(Enum):
    CHATON = "Chaton (0-6 mois)"
    ADULTE = "Adulte (6 mois - 8 ans)"
    SENIOR = "Senior (8 ans et plus)"


class DureeAdoptionStatsForm(Form):
    annee = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.value, tag.value) for tag in AnneeChoice],
        widget=Select(),
        required=False,
    )
    age = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in AgeChoice],
        widget=Select(),
        required=False,
    )

class AnneeStatsForm(Form):
    annee = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.value, tag.value) for tag in AnneeChoice],
        widget=Select(),
        required=False,
    )