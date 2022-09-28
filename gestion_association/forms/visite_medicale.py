from django.db.models import BLANK_CHOICE_DASH
from django.forms import Form, CharField, ChoiceField, Select, ModelForm, DateField

from gestion_association.forms import DateInput
from gestion_association.models.animal import Animal, StatutAnimal, TestResultChoice
from gestion_association.models.visite_medicale import TypeVisiteVetoChoice, VisiteMedicale


class VisiteMedicaleSearchForm(Form):
    veterinaire = CharField(max_length=150, required=False)
    type_visite = ChoiceField(
        choices=BLANK_CHOICE_DASH + [(tag.name, tag.value) for tag in TypeVisiteVetoChoice],
        widget=Select(),
        required=False,
        label="Type de visite",
    )
    date_min = DateField(
        label="Date de la visite médicale entre le", required=False, widget=DateInput()
    )
    date_max = DateField(label=" et le ", required=False, widget=DateInput())

statuts_association_adopte = [
    StatutAnimal.A_ADOPTER.name,
    StatutAnimal.ADOPTION.name,
    StatutAnimal.ADOPTE.name,
    StatutAnimal.ADOPTABLE.name,
    StatutAnimal.PEC.name,
    StatutAnimal.SOCIA.name,
    StatutAnimal.QUARANTAINE.name,
    StatutAnimal.SOIN.name,
    StatutAnimal.SEVRAGE.name,
]

class VisiteMedicaleForm(ModelForm):
    # Pour mettre les champs obligatoires en gras
    required_css_class = 'required'
    class Meta:
        model = VisiteMedicale
        fields = (
            "date",
            "type_visite",
            "veterinaire",
            "commentaire",
            "montant",
            "animaux",
        )

    def __init__(self, *args, **kwargs):
        super(VisiteMedicaleForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datePicker'
        self.fields['animaux'].queryset = Animal.objects.filter(inactif=False).\
            filter(statut__in=statuts_association_adopte).order_by('nom')


class TestResultsForm(Form):
    # Formulaire indiquant les résultats FIV/FELV en cas de visite médicale incluant ces tests
    fiv = ChoiceField(
        choices=[(tag.name, tag.value) for tag in TestResultChoice],
        label="Résultat test FIV",
    )
    felv = ChoiceField(
        choices=[(tag.name, tag.value) for tag in TestResultChoice],
        label="Résultat test FELV",
    )