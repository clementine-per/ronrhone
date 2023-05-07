from django.db.models import BLANK_CHOICE_DASH
from django.forms import Form, CharField, ChoiceField, Select, ModelForm, DateField

from gestion_association.forms import DateInput
from gestion_association.models.animal import Animal, StatutAnimal, TestResultChoice
from medical_visit.models import TypeVisiteVetoChoice, VisiteMedicale


class VisiteMedicaleSearchForm(Form):
    veterinary = CharField(max_length=150, required=False, label="Vétérinaire")
    visit_type = ChoiceField(
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
    StatutAnimal.ALLAITANTE.name,
]


class VisiteMedicaleForm(ModelForm):
    # Special css for mandatory fields
    required_css_class = 'required'

    class Meta:
        model = VisiteMedicale
        fields = (
            "date",
            "visit_type",
            "veterinary",
            "comment",
            "amount",
            "animals",
        )

    def __init__(self, *args, **kwargs):
        super(VisiteMedicaleForm, self).__init__(*args, **kwargs)
        self.fields['date'].widget.attrs['class'] = 'datePicker'
        self.fields['animals'].queryset = Animal.objects.filter(inactif=False).\
            filter(statut__in=statuts_association_adopte).order_by('nom')


class TestResultsForm(Form):
    # Form for FIV/FELV results if the medical visit included those tests
    fiv = ChoiceField(
        choices=[(tag.name, tag.value) for tag in TestResultChoice],
        label="Résultat test FIV",
    )
    felv = ChoiceField(
        choices=[(tag.name, tag.value) for tag in TestResultChoice],
        label="Résultat test FELV",
    )