from django.db.models import BLANK_CHOICE_DASH
from django.forms import Form, CharField, ModelForm, ChoiceField, Select

from gestion_association.models.person import Person, TypePersonChoice


class PersonSearchForm(Form):
    nom = CharField(max_length=150, required=False)
    type_person = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypePersonChoice],
        widget=Select(),
        required=False,
        label="Rôle personne",
    )


class PersonForm(ModelForm):
    class Meta:
        model = Person
        fields = (
            "prenom",
            "nom",
            "email",
            "adresse",
            "code_postal",
            "ville",
            "telephone",
            "profession",
            "commentaire",
        )


class BenevoleForm(ModelForm):
    class Meta:
        model = Person
        fields = ("commentaire_benevole",)
