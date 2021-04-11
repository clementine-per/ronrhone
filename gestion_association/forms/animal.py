from django.db.models import BLANK_CHOICE_DASH
from django.forms import (
    CharField,
    ChoiceField,
    DateField,
    DateInput,
    Form,
    ModelForm,
    ModelMultipleChoiceField,
    MultipleChoiceField,
    Select,
    SelectMultiple,
)

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import Animal, StatutAnimal, TypeChoice, statuts_association


class DateInput(DateInput):
    input_type = "date"


class AnimalSearchForm(Form):
    nom = CharField(max_length=100, required=False)
    identification = CharField(max_length=100, required=False, label="Numéro d'identification")
    type = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypeChoice],
        widget=Select(),
        required=False,
    )
    sterilise = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    date_naissance_min = DateField(
        label="Date de naissance entre le", required=False, widget=DateInput()
    )
    date_naissance_max = DateField(label=" et le ", required=False, widget=DateInput())
    date_vermifuge_min = DateField(
        label="Date du dernier vermifuge entre le", required=False, widget=DateInput()
    )
    date_vermifuge_max = DateField(label=" et le ", required=False, widget=DateInput())
    date_prochaine_visite_min = DateField(
        label="Date de prochaine visite vétérinaire entre le",
        required=False,
        widget=DateInput(),
    )
    date_prochaine_visite_max = DateField(label=" et le ", required=False, widget=DateInput())
    sans_fa = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in OuiNonChoice],
        widget=Select(),
        required=False,
    )
    statuts = MultipleChoiceField(
        choices=[(tag.name, tag.value) for tag in StatutAnimal],
        required=False,
        initial=[tag.name for tag in StatutAnimal],
    )

    def __init__(self, *args, **kwargs):
        super(AnimalSearchForm, self).__init__(*args, **kwargs)
        self.initial["statuts"] = statuts_association


class AnimalCreateForm(ModelForm):
    class Meta:
        model = Animal
        fields = (
            "nom",
            "sexe",
            "type",
            "date_naissance",
            "identification",
            "circonstances",
            "date_arrivee",
            "commentaire",
            "statut",
            "sterilise",
            "date_sterilisation",
            "primo_vaccine",
            "vaccin_ok",
            "date_dernier_vaccin",
            "date_prochain_vaccin",
            "fiv",
            "felv",
            "date_parasite",
            "lien_icad",
        )


class AnimalLinkedForm(ModelForm):
    class Meta:
        model = Animal
        fields = ("animaux_lies",)

    animaux_lies = ModelMultipleChoiceField(
        required=False,
        widget=SelectMultiple,
        queryset=Animal.objects.filter(
            statut__in=[
                StatutAnimal.A_ADOPTER.name,
                StatutAnimal.QUARANTAINE.name,
                StatutAnimal.SEVRAGE.name,
                StatutAnimal.SOCIA.name,
                StatutAnimal.SOIN.name,
            ]
        ),
    )


class AnimalInfoUpdateForm(ModelForm):
    class Meta:
        model = Animal
        fields = (
            "nom",
            "sexe",
            "type",
            "date_naissance",
            "identification",
            "circonstances",
            "date_arrivee",
            "commentaire",
            "statut",
            "lien_icad",
        )


class AnimalSanteUpdateForm(ModelForm):
    class Meta:
        model = Animal
        fields = (
            "sterilise",
            "date_sterilisation",
            "primo_vaccine",
            "vaccin_ok",
            "date_dernier_vaccin",
            "date_prochain_vaccin",
            "fiv",
            "felv",
            "date_parasite",
        )
