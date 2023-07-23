from decimal import Decimal
from difflib import get_close_matches

import requests
import json

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.shortcuts import render
from django.template.defaultfilters import slugify

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import Adoption
from gestion_association.models.animal import Animal, StatutAnimal
from gestion_association.models.person import Person
from gestion_association.views.adoption import get_montant_adoption
from gestion_association.views.utils import admin_test
# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)

api_key = settings.MONDAY_KEY
api_url = settings.MONDAY_URL
headers = {"Authorization": api_key, "API-version": "2023-04"}


@user_passes_test(admin_test)
def check_api_adoptions(request):
    selected = "monday"
    title = "Intégration avec Monday : Adoptions"

    query = get_query()
    data = {'query': query}

    r = requests.post(url=api_url, json=data, headers=headers)
    adoptions = []
    errors = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items"]
    # Chaque ligne est une adoption
    for elt in content:
        adoption = get_adoption_from_values(elt)
        if adoption == "Not Found":
            errors.append("L'animal " + elt["name"] + " n'a pas été trouvé.")
        elif adoption:
            adoptions.append(adoption)

    nb_results = len(adoptions)

    return render(request, "monday_api/adoptions_to_import.html", locals())


@user_passes_test(admin_test)
def integrate_adoptions(request):
    selected = "monday"
    title = "Intégration avec Monday : Adoptions"
    query = get_query()
    data = {'query': query}

    r = requests.post(url=api_url, json=data, headers=headers)
    if not r.ok:
        raise Exception(r.content)
    imports = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items"]
    logger.info("DEBUT Import d'adoptions")
    # Chaque ligne est une famille d'accueil
    for elt in content:
        try:
            with transaction.atomic():
                adoption = get_adoption_from_values(elt)
                if adoption == "Not Found":
                    imports.append("L'animal " + elt["name"] + " n'a pas été trouvé.")
                    logger.warning("L'animal " + elt["name"] + " n'a pas été trouvé.")
                elif adoption:
                    adoption.acompte_verse = OuiNonChoice.NON.name
                    adoption.pre_visite = OuiNonChoice.NON.name
                    adoption.visite_controle = OuiNonChoice.NON.name
                    adoption.adoptant.save()
                    adoption.animal.save()
                    adoption.save()
                    imports.append("Import de l'adoption de " + str(adoption.animal) + " par " + str(adoption.adoptant))
                    # Mise à jour du statut dans monday
                    mutation_request = get_modify_status_query(elt["id"])
                    data = {'query': mutation_request}
                    r = requests.post(url=api_url, json=data, headers=headers)
                    logger.warning("Import de l'adoption de " + str(adoption.animal) + " par " + str(adoption.adoptant))

        except Exception as e:
            imports.append("Erreur pour l'import de "+ str(adoption.adoptant) + " : " + str(e))
            logger.warning("Erreur pour l'import de l'adoptant "+ str(adoption.adoptant) + " : " + str(e))
    logger.info("FIN Import d'adoptions")
    return render(request, "monday_api/familles_import_results.html", locals())


def get_query():
    return 'query { boards(ids: [3034309911]) {\
    groups(ids: ["topics"]) {\
      items {\
        id\
        name\
        column_values(ids: ["statut", "nom___pr_nom","texte8","t_l_phone", "adresse_postale__n___rue_",\
        "code_postal", "ville", "adresse_e_mail",\
         "quels_sont_les_membres_qui_composent_votre_foyer__vous_y_compris____age__profession_etc___" \
         ]) {\
          title\
          id\
          value\
          text\
        }\
      }\
    }\
  } }'


def get_modify_status_query(item_id):
    # statut correspond à la colonne statut et l'index 0 au statut "Acompte ok"
    return 'mutation { change_column_value(item_id:' +item_id +', board_id: 3034309911,\
     column_id: "statut", value: "{\\\"index\\\":19}") {id\
  }\
}'


def get_adoption_from_values(adoption_values):
    adoption_columns = adoption_values["column_values"]
    personne = Person()
    adoption = Adoption()
    for value in adoption_columns:
        # Statut
        if value["id"] == "statut":
            # On ne veux que les adoptions dans un certain statut
            if value["text"] != "Acompte ok":
                return None

            animal_name = adoption_values["name"]
            # close_match is case sensitive
            corresponding_matches = get_close_matches(animal_name.lower(), get_animal_names(), 1)
            if not len(corresponding_matches) > 0:
                corresponding_matches = get_close_matches(animal_name.upper(), get_animal_names(), 1)
                if not len(corresponding_matches) > 0:
                    return "Not Found"
            corresponding_match = corresponding_matches[0]
            animal = Animal.objects.get(nom=corresponding_match)
        # Nom
        elif value["id"] == "nom___pr_nom":
            personne.nom = value["text"].upper()
        # Prénom
        elif value["id"] == "texte8":
            personne.prenom = value["text"]
        # Adresse
        elif value["id"] == "adresse_postale__n___rue_":
            personne.adresse = value["text"]
        # Code postal
        elif value["id"] == "code_postal":
            personne.code_postal = value["text"]
        # Ville
        elif value["id"] == "ville":
            personne.ville = value["text"]
        # Téléphone
        elif value["id"] == "t_l_phone":
            telephone = value["text"]
            if not telephone.startswith('0'):
                telephone = "+" + telephone
            personne.telephone = telephone
        # Email
        elif value["id"] == "adresse_e_mail":
            personne.email = value["text"]
        # Profesion
        elif value["id"] == "quels_sont_les_membres_qui_composent_votre_foyer__vous_y_compris____age__profession_etc___":
            personne.profession = value["text"]
    # Check si l'adoptant est déjà en base
    nom_prenom_key = f"{slugify(personne.prenom)}.{personne.nom}"
    existing_person = Person.objects.filter(nom_prenom_key=nom_prenom_key.lower())
    if existing_person:
        existing_person[0].is_adoptante = True
        adoption.adoptant = existing_person[0]
    else:
        personne.is_adoptante = True
        adoption.adoptant = personne
    adoption.animal = animal
    adoption.montant = get_montant_adoption(animal)
    if adoption.montant:
        adoption.montant_restant = adoption.montant - Decimal(100)
    return adoption


def get_animal_names():
    statuts_adoption = [
        StatutAnimal.A_ADOPTER.name,
        StatutAnimal.ADOPTION.name,
        StatutAnimal.ADOPTABLE.name,
    ]
    return list(Animal.objects.filter(statut__in=statuts_adoption).values_list('nom', flat=True))