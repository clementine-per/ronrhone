import io
import tempfile
from datetime import timedelta
from io import StringIO

import PyPDF2
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from dateutil.relativedelta import relativedelta

from gestion_association.models import OuiNonChoice
from gestion_association.models.animal import Animal, TrancheAge
from ronrhone import settings

def pieds_page(p, nb_page):
    p.setFont("Times-Italic", 0.35 * cm)
    p.setFillColor('#808080')
    p.drawString(2.7 * cm, 0.2 * cm, "Association Ron’Rhône - 98, chemin de la Combe Moussin 38270 BEAUFORT - n° SIRET : 82140540400012")
    p.setFont("Times-Bold", 0.5 * cm)
    p.setFillColor('#000000')
    p.drawString(20 * cm, 0.2 * cm, str(nb_page) + "/9")

def generation_reglement(p, difference, couleur_ronrhone, spaceStyle):
    # le paramètre "difference" arrange la position que doit avoir le contenu en fonction de s'il s'agit
    # d'un chaton ou d'un chat adulte
    # On redéfini le style 2 dans la fonction pour ajuster le texte
    style2 = ParagraphStyle(name="Style", textColor=couleur_ronrhone, fontSize=0.7 * cm, borderWidth=1, \
                            borderColor=couleur_ronrhone,
                            # haut , droite, bas, gauche
                            borderPadding=(0.01 * cm, 3.51 * cm, 0.5 * cm, 7.39 * cm))
    para = Paragraph("{} <br/>" \
                     .format("Règlement")
                     , style=style2)
    para.wrap(7 * cm, 15 * cm)
    para.drawOn(p, 9 * cm, 17 * cm + difference * cm)
    p.circle(2.5 * cm, 15.9 * cm + difference * cm, 2.5, fill=True)
    para = Paragraph("<font face='times-bold' size=14><u>PayPal</u> : </font><br/> \
                        <font face='helvetica-oblique' size=14 color='#2d8dfd'>ronrhone69@gmail.com </font><br/> \
                        <font face='helvetica-oblique' size=14>(Attention, frais de 7€ obligatoires) </font>", style=spaceStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 3 * cm, 14.5 * cm + difference * cm)
    p.circle(2.5 * cm, 13.95 * cm + difference * cm, 2.5, fill=True)
    para = Paragraph("<font face='times-bold' size=14>Lydia : </font> \
                            <font face='helvetica-oblique' size=14 color='#2d8dfd'>06. 64. 62. 32. 07.</font>")
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 3 * cm, 13.85 * cm + difference * cm)
    p.circle(2.5 * cm, 12.95 * cm + difference * cm, 2.5, fill=True)
    para = Paragraph("<font face='times-bold' size=14>Virement : </font>")
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 3 * cm, 12.85 * cm + difference * cm)
    p.setFont("Times-Bold", 0.45 * cm)
    p.setFillColor("red")
    p.drawString(11.6 * cm, 15.75 * cm + difference * cm, "Nous refusons le paiement par chèque !")
    p.setFont("Times-Bold", 0.55 * cm)
    p.drawString(11.1 * cm, 15 * cm + difference * cm, "Le restant dû devra être réglé sous 3")
    p.drawString(11.6 * cm, 14.5 * cm + difference * cm, "jours suivants la signature de ce")
    p.drawString(10.7 * cm, 14 * cm + difference * cm, "contrat, et l'animal devra être récupéré")
    p.drawString(10.8 * cm, 13.5 * cm + difference * cm, "au maximum 7 jours après la réception")
    p.drawString(10.9 * cm, 13 * cm + difference * cm, "du virement, sans quoi ce contrat sera")
    p.drawString(11.5 * cm, 12.5 * cm + difference * cm, "caduc et l'adoption annulée, sans")
    p.drawString(13.5 * cm, 12 * cm + difference * cm, "remboursement.")
    para = Paragraph("<font face='times-roman' size=14 color='red'>Merci d’indiquer le motif </font> \
                        <font face='times-bold' size=15 color='red'>« ADOPTION [NOM DE L’ANIMAL] »</font> \
                        <font face='times-roman' size=14 color='red'>, faute de quoi, 48h de \
                        carence dans le processus d’adoption seront mises en place afin de recouper les infos.</font>"
                        ,style=spaceStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 2.25 * cm, 9.5 * cm + difference * cm)
    p.drawImage(settings.STATIC_ROOT + "/img/RIB.png",
                0.75 * cm, 1 * cm + difference * cm, width=19.5 * cm, height=8 * cm, mask="auto")

@login_required
def generate_contract(request, pk):
    nb_page = 0
    animal = Animal.objects.get(pk=pk)
    is_enfant = animal.tranche_age == TrancheAge.ENFANT.name
    couleur_ronrhone = "#00bfff"
    temp_file = tempfile.NamedTemporaryFile()
    p = canvas.Canvas(temp_file)
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
    p.drawString(2 * cm, 20.5 * cm, "Téléphone : " + animal.adoptant.telephone)
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
    # Bullet de début de paragraphe
    p.circle(3.5 * cm, 28.55 * cm, 2.5, fill=True)
    p.drawString(4 * cm, 28.4 * cm, "Le prochain rappel de vaccin de " + animal.nom + " est à faire :")
    # Determiner la date du prochain vaccin
    if animal.date_prochain_vaccin:
        prochain_vaccin = animal.date_prochain_vaccin
        prochain_vaccin_str = prochain_vaccin.strftime("%d/%m/%Y")
    elif animal.date_dernier_vaccin:
        if animal.vaccin_ok == OuiNonChoice.OUI.name:
            prochain_vaccin = animal.date_dernier_vaccin + relativedelta(years=1)
        else :
            prochain_vaccin = animal.date_dernier_vaccin + relativedelta(months=1)
        prochain_vaccin_str = prochain_vaccin.strftime("%d/%m/%Y")
    else:
        prochain_vaccin_str = "__/__/__"
    if animal.vaccin_ok == OuiNonChoice.OUI.name:
        p.drawString(5.5 * cm, 27.5 * cm, "peu de temps avant le " +
                     prochain_vaccin_str + ".")
    else:
        vaccin_delai = prochain_vaccin + relativedelta(days=7)
        p.drawString(5.5 * cm, 27.5 * cm, "entre le " + prochain_vaccin_str +
                     " et le " + vaccin_delai.strftime("%d/%m/%Y") + ".")
    # On ne peut pas faire autrement qu'avec les paragraphes pour souligner du texte optimalement
    para = Paragraph("<font face='times-bold' size=14><u> {} </u></font> <br/>" \
                     .format("Attention, ce rappel sera à votre charge !"))
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 3.75 * cm, 26.3 * cm)

    # Style de paragraphes avec un espace entre les lignes
    spaceStyle = ParagraphStyle(name='spaceStyle', leading=17)

    # On anticipe le pieds de page à cause des conditions qui prennent sur plus d'une page
    # pieds de page
    nb_page += 1
    pieds_page(p, nb_page)

    # Dans le cas d'un chaton
    if is_enfant:
        p.circle(3.5 * cm, 25.45 * cm, 2.5, fill=True)
        para = Paragraph("<font face='helvetica' size=12> {} </font> \
            <font face='times-bolditalic' size=14><u> {} </u></font> <br/> \
            <font face='helvetica' size=12> {} </font>" \
                         .format("La stérilisation du chaton devra être effectuée ", "OBLIGATOIREMENT", "avant ses 7 mois, soit :"))
        para.wrap(14 * cm, 15 * cm)
        para.drawOn(p, 4 * cm, 25 * cm)
        para = Paragraph(
            "<font face='helvetica' size=12> - </font><font face='helvetica-oblique' size=12> \
            <u> {} </u></font><font face='helvetica' size=12> {} </font> <br/> \
            <font face='helvetica' size=12> {} </font> <br/> <font face='helvetica' size=12> - </font> \
            <font face='helvetica-oblique' size=12><u> {} </u></font> \
            <font face='helvetica' size=12> {} </font>" \
            .format("Chez un de nos vétérinaires partenaires ",
                    "grâce à un bon de stérilisation",
                    "(d’une valeur de 45€ pour un mâle et 80€ pour une femelle).",
                    "Par vos propres moyens", ", chez le vétérinaire de votre choix."), style=spaceStyle)
        para.wrap(14 * cm, 15 * cm)
        para.drawOn(p, 4 * cm, 23 * cm)
        p.circle(3.5 * cm, 22.5 * cm, 2.5, fill=True)
        para = Paragraph("<font face='helvetica' size=12>Un chèque de caution d’un montant de \
            <font color=red>150€</font> sera demandé à l’adoption <br/> \
            et restitué à réception d’un certificat de stérilisation. </font>")
        para.wrap(14 * cm, 15 * cm)
        para.drawOn(p, 4 * cm, 22 * cm)
        p.circle(3.5 * cm, 21.4 * cm, 2.5, fill=True)
        para = Paragraph("<font face='helvetica' size=12>Si l’Association ne reçoit pas de certificat de stérilisation avant <br/> \
                    l’anniversaire des 7 mois du chaton, soit le {}, elle se réserve le<br/> \
                    droit de récupérer le chaton sans remboursement d’aucun frais engagé \
                    par l’adoptant et d’encaisser le chèque de caution éventuel</font>" \
                         .format((animal.date_naissance + relativedelta(months=7)).strftime("%d/%m/%Y")))
        para.wrap(14 * cm, 15 * cm)
        para.drawOn(p, 4 * cm, 20 * cm)
        p.circle(3.5 * cm, 19 * cm, 2.5, fill=True)
        para = Paragraph("<font face='helvetica' size=12>Environ deux mois après l’adoption, l’Association prendra rendez-vous <br/> \
                    avec vous pour une visite de contrôle, effectuée par un membre de <br/> \
                    l’Association. </font>")
        para.wrap(14 * cm, 15 * cm)
        para.drawOn(p, 4 * cm, 18 * cm)

        # La suite est la même sur les deux modèles mais pas au même endroit, donc on définit une méthode
        generation_reglement(p, 0, couleur_ronrhone, spaceStyle)

        # Redéfinition de la différence
        # TODO : Vraie différence
        #difference = 1

    # Si c'est un chat adulte
    else:
        style3 = ParagraphStyle(name="Style", textColor=couleur_ronrhone, fontSize=0.7 * cm, borderWidth=1, \
                                borderColor=couleur_ronrhone,
                                # haut , droite, bas, gauche
                                borderPadding=(0.01 * cm, 0.05 * cm, 0.5 * cm, 4.95 * cm))
        para = Paragraph("{} <br/>" \
                         .format("Pièces à joindre au contrat")
                         , style=style3)
        para.wrap(13 * cm, 15 * cm)
        para.drawOn(p, 6.5 * cm, 25.5 * cm)
        p.setFont("Helvetica", 0.5 * cm)
        p.drawString(3 * cm, 24 * cm, "✓ Photocopie de votre pièce d'identité")
        p.drawString(3 * cm, 23.3 * cm, "✓ Photocopie d'un justificatif de domicile de moins de 3 mois")
        generation_reglement(p, 5, couleur_ronrhone, spaceStyle)

        # Redéfinition de la différence
        # TODO : Vraie différence
        #difference = 1

        # TODO :Génération de la fin de la page

    p.showPage()

    # Finalisation
    p.save()

    # Merge entre la partie écrite ci-dessus et les pages pdf fixes à ajouter à la suite
    if is_enfant:
        contrat_fixe = open(settings.STATIC_ROOT + "/pdf/contrat_chaton.pdf", 'rb')
    else:
        contrat_fixe = open(settings.STATIC_ROOT + "/pdf/contrat_adulte.pdf", 'rb')
    # Fichier temporaire contenant le contenu généré
    pdf1Reader = PyPDF2.PdfFileReader(temp_file)
    pdf2Reader = PyPDF2.PdfFileReader(contrat_fixe)
    pdfWriter = PyPDF2.PdfFileWriter()
    for pageNum in range(pdf1Reader.numPages):
        pageObj = pdf1Reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)
    for pageNum in range(pdf2Reader.numPages):
        pageObj = pdf2Reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)
    pdfOutputFile = tempfile.NamedTemporaryFile()
    pdfWriter.write(pdfOutputFile)
    pdfOutputFile.flush()
    pdfOutputFile.seek(0)
    content = pdfOutputFile.read()
    contrat_fixe.close()
    pdfOutputFile.close()

    # Create the HttpResponse object
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Contrat_{}_{}.pdf"'.format(animal.nom, animal.id)

    return response