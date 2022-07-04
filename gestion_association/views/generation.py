from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle

from gestion_association.models.animal import Animal, TrancheAge
from ronrhone import settings

def pieds_page(p, nb_page):
    p.setFont("Times-Italic", 0.35 * cm)
    p.setFillColor('#808080')
    p.drawString(2.7 * cm, 0.2 * cm, "Association Ron’Rhône - 98, chemin de la Combe Moussin 38270 BEAUFORT - n° SIRET : 82140540400012")
    p.setFont("Times-Bold", 0.5 * cm)
    p.setFillColor('#000000')
    p.drawString(20 * cm, 0.2 * cm, str(nb_page) + "/9")


@login_required
def generate_contract(request, pk):
    nb_page = 0
    animal = Animal.objects.get(pk=pk)
    is_enfant = animal.tranche_age == TrancheAge.ENFANT.name
    couleur_ronrhone = "#2d8dfd"
    # Create the HttpResponse object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Contrat_{}_{}.pdf"'.format(animal.nom, animal.id)
    p = canvas.Canvas(response)
    #logo en-tete
    p.drawImage(settings.STATIC_ROOT + "/img/logo.png",
                0.75 * cm, 23.25 * cm, width=5.5 * cm, height=5.5 * cm, mask="auto")
    # Type de contrat, en haut à droite
    p.drawImage(settings.STATIC_ROOT + "/img/entete.png",
                14 * cm, 27.5 * cm, width=15 * cm, height=2.5 * cm, mask="auto")
    p.setFont("Times-Italic", 0.5 * cm)
    if is_enfant:
        p.drawString(18 * cm, 29 * cm, "CHATON")
    else:
        p.drawString(18 * cm, 29 * cm, "ADULTE")
    # Titre
    style = ParagraphStyle(name="Style", textColor=couleur_ronrhone, fontSize=0.8*cm, borderWidth=2, \
                           borderColor=couleur_ronrhone,
                           borderRadius=0.2 * cm,
                           borderPadding=(0.2 * cm, 0.5 * cm, 1.5 * cm, 0.5 * cm))

    para = Paragraph("{} <br/><br/> {} <br/>" \
                     .format("Contrat d'adoption de ", animal.nom)
                     , style=style)
    para.wrap(8 * cm, 7 * cm)
    para.drawOn(p, 8.5 * cm, 26 * cm)

    # Informations personnelles de l'adoptant
    # Mise en place du style2 pour les sous-titres
    style2 = ParagraphStyle(name="Style", textColor=couleur_ronrhone, fontSize=0.7 * cm, borderWidth=1, \
                           borderColor=couleur_ronrhone,
                            # haut , droite, bas, gauche
                           borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))

    para = Paragraph("{} <br/>" \
                     .format("Informations personnelles de l'adoptant")
                     , style=style2)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, 22.5 * cm)
    p.setFont("Times-Bold", 0.5 * cm)
    p.drawString(2 * cm, 21.3 * cm, "Nom : " + animal.adoptant.nom)
    p.drawString(11 * cm, 21.3 * cm, "Prénom : " + animal.adoptant.prenom)
    p.drawString(2 * cm, 20.5 * cm, "Date de naissance : " + "00/00/0000")
    p.drawString(11 * cm, 20.5 * cm, "Téléphone : " + animal.adoptant.telephone)
    p.drawString(2 * cm, 19.7 * cm, "Adresse postale : " + animal.adoptant.adresse)
    p.drawString(2 * cm, 18.9 * cm, "Code Postal : " + animal.adoptant.code_postal)
    p.drawString(6.75 * cm, 18.9 * cm, "Ville : " + animal.adoptant.ville)
    p.drawString(2 * cm, 18.1 * cm, "Adresse e-mail : " + animal.adoptant.email)
    p.drawString(2 * cm, 17.3 * cm, "Profession : " + animal.adoptant.profession)

    # Checkbox
    styleSquare = ParagraphStyle(name="Style", borderWidth=1, borderColor="#000000",
                           borderPadding=(0.2 * cm, 0.1 * cm, 0.2 * cm, 0.1 * cm))
    para = Paragraph(" ", style=styleSquare)
    para.wrap(0.2 * cm, 1 * cm)
    para.drawOn(p, 2.2 * cm, 16.5 * cm)

    p.setFont("Helvetica", 0.5 * cm)
    p.drawString(3 * cm, 16.3 * cm, "Moi, l'adoptant déclare consentir à ce que l’Association Ron’Rhône")
    p.drawString(2 * cm, 15.65 * cm, "transmette ce contrat d’adoption à la Fondation Capellino / Almo Nature,")
    p.drawString(2 * cm, 15.0 * cm, "dans le cadre de la bonne mise en œuvre du projet Companion Animal For")
    p.drawString(2 * cm, 14.35 * cm, "Life, dont l’Association est partenaire et uniquement dans ce cadre. Plus")
    p.drawString(2 * cm, 13.7 * cm, "d'informations sur https://www.almonature.com/fr/companion-animal-for-life/")

    para = Paragraph("{} <br/>" \
                     .format("Informations sur le pensionnaire adopté")
                     , style=style2)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, 12.5 * cm)

    p.setFont("Times-Roman", 0.5 * cm)
    p.drawString(2 * cm, 11.35 * cm, "- Identification : " + animal.identification)
    p.drawString(11 * cm, 11.35 * cm, "- Test FeLV : " + animal.felv)
    if is_enfant:
        p.drawString(2 * cm, 10.75 * cm, "- Nom du chaton : " + animal.nom)
    else:
        p.drawString(2 * cm, 10.75 * cm, "- Nom du chat : " + animal.nom)
    p.drawString(11 * cm, 10.75 * cm, "- Test FIV : " + animal.fiv)
    p.drawString(2 * cm, 10.15 * cm, "- Sexe : " + animal.sexe)
    p.drawString(11 * cm, 10.15 * cm, "- Race : " + animal.type)
    p.drawString(2 * cm, 9.55 * cm, "- Date de naissance : " + animal.date_naissance.strftime("%d/%m/%Y"))
    p.drawString(11 * cm, 9.55 * cm, "- Robe : ")
    p.drawString(2 * cm, 8.95 * cm, "- Signes particuliers : ")

    p.setFont("Helvetica", 1 * cm)
    # CHATON
    if is_enfant:
        # TODO : Mettre vraiment les frais d'adoption
        elements = [["Les frais d'adoption sont de " + animal.get_montant_veto_total() + " euros.", ''],
                    ["(majoration de ", '20€ pour une primo-vaccination leucose,'],
                    ["", '40€ pour une vaccination leucose à jour).'],
                    ["", ''],
                    ["Cette somme correspond au remboursement des frais vétérinaires", ''],
                    ["qui incluent les prestations suivantes : ", ''],
                    ["", '- Identification par puce électronique'],
                    ["", '- Test FIV / FeLV'],
                    ["", '- Primo vaccination'],
                    ["", '- Anti-parasitaires'],
                    ["", '- Certificat de bonne santé']]
        tableau = Table(elements, colWidths=[2.75 * cm, 14.25 * cm])
        # part de en haut à gauche !
        # tableau pour faire le cadre mais également la séparation avant la somme des vaccinations
        tableau.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, - 1), 0.75, colors.black),
            ('BOX', (1, 1), (-2, -9), 0.75, colors.black),
        ]))

        tableau.wrap(18 * cm, 20 * cm)
        tableau.drawOn(p, 2 * cm, 1 * cm)
    # ADULTE
    else:
        elements = [[Paragraph("Chat femelle Primo"), Paragraph("Identification + Stérilisation + Primo vaccin + Test FIV/FELV + Déparasitant + Vermifuge"), "170€"],
                    [Paragraph("Chat femelle Primo + Rappel"), Paragraph("Identification + Stérilisation + Vaccins à jour + Test FIV/FELV + Déparasitant + Vermifuge"), "200€"],
                    [Paragraph("Chat mâle Primo"), Paragraph("Identification + Castration + Primo vaccin + Test FIV/FELV + Déparasitant + Vermifuge"), "150€"],
                    [Paragraph("Chat mâle Primo + Rappel"), Paragraph("Identification + Castration + Vaccins à jour + Test FIV/FELV + Déparasitant + Vermifuge"), "180€"]]
        tableau = Table(elements, colWidths=[3 * cm, 12 * cm, 2 * cm])
        tableau.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, - 1), 0.75, colors.black),
            ('INNERGRID', (0, 0), (-1, - 1), 0.75, colors.black),
        ]))

        tableau.wrap(18 * cm, 20 * cm)
        tableau.drawOn(p, 2 * cm, 4 * cm)

        elements = [["(majoration de ", '20€ pour une primo-vaccination leucose,'],
                    ["", '40€ pour une vaccination leucose à jour).']]
        tableau = Table(elements, colWidths=[2.75 * cm, 14.25 * cm])
        # tableau pour faire la séparation avant la somme des vaccinations
        # On établi le cadre en noir puis le cadre total du tableau en blanc pour effacer le contour
        tableau.setStyle(TableStyle([
            ('BOX', (0, 0), (-1, - 1), 0.75, colors.white),
            ('BOX', (1, 0), (-2, -1), 0.75, colors.black),
        ]))

        tableau.wrap(18 * cm, 20 * cm)
        tableau.drawOn(p, 2 * cm, 2.5 * cm)

    # pieds de page
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    #Page 2
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    # Page 3
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    # Page 4
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    # Page 5
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    # Page 6
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    # Page 7
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    # Page 8
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    # Page 9
    nb_page += 1
    pieds_page(p, nb_page)

    # Finalisation
    p.save()
    return response