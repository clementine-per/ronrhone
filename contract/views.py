from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


from contract.utils import *
from gestion_association.models.animal import Animal, TrancheAge

@login_required
def generate_contract(request, pk):
    # Animal data
    animal = Animal.objects.get(pk=pk)
    is_child = animal.tranche_age == TrancheAge.ENFANT.name
    # Données pour créer le pdf
    nb_page = 1
    temp_file = tempfile.NamedTemporaryFile()
    p = canvas.Canvas(temp_file)
    p.setFont("Helvetica", 1 * cm)

    # En-tête du contrat
    header(p, animal)

    # Informations personnelles de l'adoptant
    personal_infos(p, animal)

    # Informations pensionnaire
    infos_animal(p, animal)

    # Info frais d'adoption
    info_prices(p,animal)

    nb_page = next_page(p, nb_page)

    #Page 2

    # Infos rappel vaccin
    info_vaccine_shot(p, animal)


    # Dans le cas d'un chaton
    if is_child:
        if animal.sterilise == OuiNonChoice.NON.name:
            # Infos sterilisation chaton
            info_sterilisation(p, spaceStyle, animal)

        # La suite est la même sur les deux modèles mais pas au même endroit, donc on définit une méthode
        generation_payment(p, 0, animal)

    # Si c'est un chat adulte
    else:
        generation_payment(p, 8, animal)
        food_info(p, animal, 8)

    next_page(p, nb_page)

    # Page 3

    if is_child:
        food_info(p, animal, 28)
        engagement(p, animal, 23)
        amounts(p,animal,4)
        next_page(p, nb_page)
        # Page 4 contrat chatons
        contract_pieces(p, 28)
        signatures(p, 20)
    else:
        engagement(p, animal, 28)
        amounts(p, animal, 8.5)
        contract_pieces(p, 7.8)
        signatures(p, 1)

    next_page(p, nb_page)

    # Finalisation
    p.save()

    # Merge entre la partie écrite ci-dessus et les pages pdf fixes à ajouter à la suite
    content = create_complete_pdf(temp_file, animal)

    # Create the HttpResponse object
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Contrat_{}_{}.pdf"'.format(animal.nom, animal.id)

    return response
