from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponse


from contract.utils import *
from gestion_association.models.animal import Animal, TrancheAge
from gestion_association.views.utils import admin_test


@user_passes_test(admin_test)
def generate_contract(request, pk):
    # Animal data
    animal = Animal.objects.get(pk=pk)
    is_child = animal.tranche_age == TrancheAge.ENFANT.name
    # Data for the canvas (reportlab)
    nb_page = 1
    temp_file = tempfile.NamedTemporaryFile()
    p = canvas.Canvas(temp_file)
    p.setFont("Helvetica", 1 * cm)

    # Contract header
    header(p, animal)

    # Adoptant's personal informations
    personal_infos(p, animal)

    # Informations of the animal
    infos_animal(p, animal)

    # Info adoption amount
    info_prices(p,animal)

    nb_page = next_page(p, nb_page)

    #Page 2

    # Infos for the next vaccine
    info_vaccine_shot(p, animal)


    # For a kitten
    if is_child:
        if animal.sterilise == OuiNonChoice.NON.name:
            # Infos sterilisation kitten
            info_sterilisation(p, animal)
        generation_payment(p, 0, animal)

    # For an adult cat
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
        # Page 4 kitten contract
        contract_pieces(p, 28)
        signatures(p, 20)
    else:
        engagement(p, animal, 28)
        amounts(p, animal, 8.5)
        contract_pieces(p, 7.8)
        signatures(p, 1)

    next_page(p, nb_page)

    # Finalize the canvas
    p.save()

    # Merge generated part and fixed part to add at the end
    content = create_complete_pdf(temp_file, animal)

    # Create the HttpResponse object
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Contrat_{}_{}.pdf"'.format(animal.nom, animal.id)

    return response
