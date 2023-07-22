import requests
import json

from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.db import transaction
from django.shortcuts import render

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import Preference
from gestion_association.models.famille import Famille
from gestion_association.models.person import Person
from gestion_association.views.utils import admin_test

api_key = settings.MONDAY_KEY
api_url = settings.MONDAY_URL
headers = {"Authorization": api_key, "API-version": "2023-04"}


@user_passes_test(admin_test)
def check_api_fa(request):
    selected = "monday"
    title = "Intégration avec Monday : Familles d'accueil"

    query = get_query()
    data = {'query': query}

    r = requests.post(url=api_url, json=data, headers=headers)
    familles = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items"]
    # Chaque ligne est une famille d'accueil
    for fa in content:
        famille = get_fa_from_values(fa)
        if famille:
            familles.append(famille)
    nb_results = len(familles)

    return render(request, "monday_api/familles_to_import.html", locals())


@user_passes_test(admin_test)
def integrate_fa(request):
    selected = "monday"
    title = "Intégration avec Monday : Familles d'accueil"
    query = get_query()
    data = {'query': query}

    r = requests.post(url=api_url, json=data, headers=headers)
    if not r.ok:
        raise Exception(r.content)
    imports = []
    # On récupère les lignes du tableau
    content = json.loads(r.content)["data"]["boards"][0]["groups"][0]["items"]
    # Chaque ligne est une famille d'accueil
    for fa in content:
        try:
            with transaction.atomic():
                famille = get_fa_from_values(fa)
                if famille:
                    famille.personne.save()
                    famille.preference.save()
                    famille.save()
                    imports.append("Import famille d'accueil de " + str(famille.personne))

                    # Mise à jour du statut dans monday
                    mutation_request = get_modify_status_query(fa["id"])
                    data = {'query': mutation_request}
                    r = requests.post(url=api_url, json=data, headers=headers)

        except Exception as e:
            imports.append("Erreur pour l'import de "+ str(famille.personne) + " : " + str(e))

    return render(request, "monday_api/familles_import_results.html", locals())


def get_query():
    return 'query { boards(ids: [3040453225]) {\
    groups(ids: ["1659706411_reponses_fa"]) {\
      items {\
        id\
        name\
        column_values(ids: ["statut96", "texte9","s_lection_multiple","chiffre3", "statut_11",\
        "s_lection_unique1", "s_lection_unique11", "s_lection_unique", "case___cocher2",\
         "s_lection_unique88", "statut_1", "court_texte7", "texte", \
         "texte3", "texte2", "texte1", "texte5", "texte8", "t_l_phone", "e_mail",\
          "texte2","statut"]) {\
          title\
          id\
          value\
          text\
        }\
      }\
    }\
  } }'


def get_modify_status_query(item_id):
    # statut96 correspond à la colonne statut et l'index 3 au statut "Enregistré dans l'appli"
    return 'mutation { change_column_value(item_id:' +item_id +', board_id: 3040453225,\
     column_id: "statut96", value: "{\\\"index\\\":3}") {id\
  }\
}'


def get_fa_from_values(fa_values):
    fa_columns = fa_values["column_values"]
    personne = Person()
    famille = Famille()
    famille.commentaire = ""
    preference = Preference()
    for value in fa_columns:
        # Statut
        if value["id"] == "statut96":
            # On ne veux que les FA à intégrer
            if value["text"] != "À intégrer":
                return None
        # Nom
        elif value["id"] == "texte":
            personne.nom = value["text"].upper()
        # Prénom
        elif value["id"] == "texte3":
            personne.prenom = value["text"]
        # Adresse
        elif value["id"] == "texte1":
            personne.adresse = value["text"]
        # Code postal
        elif value["id"] == "texte5":
            personne.code_postal = value["text"]
        # Ville
        elif value["id"] == "texte8":
            personne.ville = value["text"].upper()
        # Téléphone
        elif value["id"] == "t_l_phone":
            telephone = value["text"]
            if not telephone.startswith('0'):
                telephone = "+" + telephone
            personne.telephone = telephone
        # Email
        elif value["id"] == "e_mail":
            personne.email = value["text"]
        # FA - Commentaire
        elif value["id"] == "statut":
            famille.commentaire = famille.commentaire + " " + value["text"]
            if value["text"].find("jardin") > 0:
                preference.exterieur = OuiNonChoice.OUI.name
        elif value["id"] == "texte2":
            famille.commentaire = famille.commentaire + " " + value["text"]
        # FA - Animaux de la FA
        elif value["id"] == "case___cocher2":
            famille.autres_animaux = value["text"]
        # FA - Nombre de places
        elif value["id"] == "chiffre3":
            famille.nb_places = int(value["text"])
        # FA - Détail des accueils acceptés
        elif value["id"] == "s_lection_multiple":
            famille.detail_places = value["text"]
        # FA - Accepte les accueils de longue durée
        # FA - Sociabilisation
        elif value["id"] == "s_lection_unique":
            if value["text"]:
                preference.sociabilisation = OuiNonChoice.OUI.name
        # FA - Extérieur
        # FA - Quarantaine
        elif value["id"] == "statut_1":
            if value["text"] == 'OUI':
                preference.quarantaine = OuiNonChoice.OUI.name
        # FA - Biberonnage
        elif value["id"] == "s_lection_unique11":
            if value["text"]:
                preference.biberonnage = OuiNonChoice.OUI.name
    personne.is_famille = True
    famille.personne = personne
    famille.preference = preference
    return famille


