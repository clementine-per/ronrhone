from django.forms import ModelForm, ChoiceField, Form

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import Adoption, BonSterilisation
from gestion_association.models.animal import Animal, StatutAnimal


class AdoptionCreateFormNoAdoptant(ModelForm):
    class Meta:
        model = Adoption
        fields = (
            "date",
            "acompte_verse",
            "montant",
            "montant_restant",
            "pre_visite",
            "visite_controle",
            "personne_visite",
            "date_visite",
        )


class AdoptionCreateForm(ModelForm):
    class Meta:
        model = Adoption
        fields = (
            "date",
            "acompte_verse",
            "adoptant",
            "montant",
            "montant_restant",
            "pre_visite",
            "visite_controle",
            "personne_visite",
            "date_visite",
        )


class AdoptionFromUserForm(ModelForm):
    class Meta:
        model = Adoption
        fields = (
            "date",
            "acompte_verse",
            "animal",
            "montant",
            "montant_restant",
            "pre_visite",
            "visite_controle",
            "personne_visite",
            "date_visite",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["animal"].queryset = Animal.objects.filter(
            statut=StatutAnimal.A_ADOPTER.name
        )


class AdoptionUpdateForm(ModelForm):
    class Meta:
        model = Adoption
        fields = (
            "date",
            "acompte_verse",
            "montant",
            "montant_restant",
            "pre_visite",
            "visite_controle",
            "personne_visite",
            "date_visite",
        )


class ShowBonForm(Form):
    # Champ indiquant si on doit afficher le formulaire de bon de stérilisation
    show = ChoiceField(
        choices=[(tag.name, tag.value) for tag in OuiNonChoice],
        label="Bon de stérilisation",
    )


class BonSterilisationForm(ModelForm):
    class Meta:
        model = BonSterilisation
        fields = ("date_max", "envoye", "utilise", "date_utilisation")
