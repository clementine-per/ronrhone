import io
import tempfile
from decimal import Decimal

import PyPDF2
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils import timezone
from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from dateutil.relativedelta import relativedelta

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import Adoption
from gestion_association.models.animal import Animal, TrancheAge, SexeChoice
from django.conf import settings

# Couleurs et styles pour la génération PDF
couleur_ronrhone = "#00bfff"
blackParagraphStyle = ParagraphStyle(name="Black", textColor="black", alignement=TA_JUSTIFY, fontSize=0.5*cm,
                            fontName = "Helvetica", borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))
redParagraphStyle = ParagraphStyle(name="Red", textColor="red", alignement=TA_JUSTIFY, fontSize=0.5*cm,
                            fontName = "Helvetica", borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))
blueParagraphStyle = ParagraphStyle(name="Blue", textColor=couleur_ronrhone, alignement=TA_JUSTIFY, fontSize=0.5*cm,
                            fontName = "Helvetica", borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))
# Mise en place du style2 pour les sous-titres
titleStyle = ParagraphStyle(name="Style", textColor=couleur_ronrhone, fontSize=0.7 * cm, borderWidth=1, \
                        borderColor=couleur_ronrhone,
                        # haut , droite, bas, gauche
                        borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))

@login_required
def generate_contract(request, pk):
    nb_page = 0
    animal = Animal.objects.get(pk=pk)
    is_enfant = animal.tranche_age == TrancheAge.ENFANT.name
    temp_file = tempfile.NamedTemporaryFile()
    p = canvas.Canvas(temp_file)

    # En-tête du contrat
    en_tete(p, is_enfant, animal)

    # Informations personnelles de l'adoptant
    infos_personnelles(p, animal)

    # Informations pensionnaire
    infos_pensionnaire(p, animal, is_enfant)


    p.setFont("Helvetica", 1 * cm)
    # CHATON
    if is_enfant:
        # Info frais d'adoption chaton
        info_tarifs_chatons(p, animal)
    # ADULTE
    else:
        # Infos tarifs adultes
        info_tarifs_adulte(p)
    # pieds de page
    nb_page += 1
    pieds_page(p, nb_page)

    # Changement de page
    p.showPage()

    #Page 2

    # pieds de page
    nb_page += 1
    pieds_page(p, nb_page)

    # Infos rappel vaccin
    info_rappel_vaccin(p, animal)

    # Style de paragraphes avec un espace entre les lignes
    spaceStyle = ParagraphStyle(name='spaceStyle', leading=17)


    # Dans le cas d'un chaton
    if is_enfant:
        if animal.sterilise == OuiNonChoice.NON.name:
            # Infos sterilisation chaton
            info_sterilisation(p, spaceStyle, animal)

        # La suite est la même sur les deux modèles mais pas au même endroit, donc on définit une méthode
        generation_reglement(p, 0, spaceStyle, animal)

    # Si c'est un chat adulte
    else:
        generation_reglement(p, 8, spaceStyle, animal)
        exigences_alimentaires(p, animal, 8)

    p.showPage()

    # Page 3
    # pieds de page
    nb_page += 1
    pieds_page(p, nb_page)

    if is_enfant:
        exigences_alimentaires(p, animal, 28)
        engagement(p, animal, 23)
        montants(p,animal,4)
        # Page 4 contrat chatons
        p.showPage()
        nb_page += 1
        pieds_page(p, nb_page)
        pieces_contrat(p, 28)
        signatures(p, 20)
    else:
        engagement(p, animal, 28)
        montants(p, animal, 8.5)
        pieces_contrat(p, 7.8)
        signatures(p, 1)

    p.showPage()

    # Finalisation
    p.save()

    # Merge entre la partie écrite ci-dessus et les pages pdf fixes à ajouter à la suite
    if is_enfant:
        contrat_fixe = open(settings.STATIC_ROOT + "/pdf/contrat_chaton.pdf", 'rb')
    else:
        contrat_fixe = open(settings.STATIC_ROOT + "/pdf/contrat_adulte.pdf", 'rb')
    certificat_engagement = open(settings.STATIC_ROOT + "/pdf/certificat-engagement.pdf", 'rb')
    # Fichier temporaire contenant le contenu généré
    pdf1Reader = PyPDF2.PdfFileReader(temp_file)
    pdf2Reader = PyPDF2.PdfFileReader(contrat_fixe)
    certificat_engagement_data = get_data_certificat_engagement(animal)
    pdf3Reader = PyPDF2.PdfFileReader(certificat_engagement)
    pdfWriter = PyPDF2.PdfFileWriter()
    for pageNum in range(pdf1Reader.numPages):
        pageObj = pdf1Reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)
    for pageNum in range(pdf2Reader.numPages):
        pageObj = pdf2Reader.getPage(pageNum)
        pdfWriter.addPage(pageObj)
    for pageNum in range(pdf3Reader.numPages):
        pageObj = pdf3Reader.getPage(pageNum)
        if pageNum == 0:
            new_pdf = PyPDF2.PdfFileReader(certificat_engagement_data)
            pageObj.mergePage(new_pdf.getPage(0))
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

def get_data_certificat_engagement(animal):
    result_bytes = io.BytesIO()
    certificat_canvas = canvas.Canvas(result_bytes)
    certificat_canvas.setFont("Helvetica", 0.4 * cm)
    certificat_canvas.drawString(3.6 * cm, 24 * cm, animal.adoptant.prenom)
    certificat_canvas.drawString(3.4 * cm, 23.5 * cm, animal.adoptant.nom)
    certificat_canvas.drawString(3.5 * cm, 23 * cm, animal.adoptant.adresse)
    certificat_canvas.drawString(2 * cm, 22.45 * cm, animal.adoptant.code_postal + " " + animal.adoptant.ville)
    certificat_canvas.drawString(3.5 * cm, 21.9 * cm, animal.adoptant.email)
    certificat_canvas.save()
    result_bytes.seek(0)
    return result_bytes

def pieces_contrat(p, vertical):
    para = Paragraph("{} <br/>" \
                     .format("Pièces à joindre au contrat")
                     , style=titleStyle)
    para.wrap(13 * cm, 15 * cm)
    para.drawOn(p, 4.5 * cm, vertical * cm)
    p.setFont("Helvetica", 0.5 * cm)
    p.drawString(2 * cm, (vertical - 1.2) * cm, "✓ Photocopie de votre pièce d'identité")
    p.drawString(2 * cm, (vertical - 1.7) * cm, "✓ Photocopie d'un justificatif de domicile de moins de 3 mois")


def pieds_page(p, nb_page):
    p.setFont("Times-Italic", 0.35 * cm)
    p.setFillColor('#808080')
    p.drawString(2.7 * cm, 0.2 * cm, "Association Ron’Rhône - 98, chemin de la Combe Moussin 38270 BEAUFORT - n° SIRET : 82140540400012")
    p.setFont("Times-Bold", 0.5 * cm)
    p.setFillColor('#000000')
    p.drawString(20 * cm, 0.2 * cm, str(nb_page) + "/9")


def generation_reglement(p, difference, spaceStyle, animal):
    # le paramètre "difference" arrange la position que doit avoir le contenu en fonction de s'il s'agit
    # d'un chaton ou d'un chat adulte
    # On redéfini le style 2 dans la fonction pour ajuster le texte
    para = Paragraph("{} <br/>" \
                     .format("Règlement")
                     , style=titleStyle)
    para.wrap(7 * cm, 15 * cm)
    para.drawOn(p, 4.5 * cm, 17 * cm + difference * cm)
    p.circle(2.5 * cm, 15.4 * cm + difference * cm, 2.5, fill=True)
    para = Paragraph("<font face='times-bold' size=14><u>Paylib ou Lydia :</u>  </font><br/> \
                        <font face='helvetica-oblique' size=14 color='#2d8dfd'>06. 64. 62. 32. 07.</font>", style=spaceStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 3 * cm, 14.5 * cm + difference * cm)
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
    para = Paragraph("<font face='Helvetica' size=14 color='red'>Merci d’indiquer le motif </font> \
                        <font face='times-bold' size=15 color='red'>« ADOPTION " +
                     animal.nom + " »</font> \
                        <font face='Helvetica' size=14 color='red'>, faute de quoi, 48h de \
                        carence dans le processus d’adoption seront mises en place afin de recouper les infos.</font>"
                        ,style=spaceStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 2.25 * cm, 9.5 * cm + difference * cm)
    p.drawImage(settings.STATIC_ROOT + "/img/RIB.PNG",
                0.75 * cm, 1 * cm + difference * cm, width=19.5 * cm, height=8 * cm, mask="auto")


def en_tete(p, is_enfant, animal):
    # logo en-tete
    p.drawImage(settings.STATIC_ROOT + "/img/logo.PNG",
                0.75 * cm, 23.25 * cm, width=5.5 * cm, height=5.5 * cm, mask="auto")
    # Type de contrat, en haut à droite
    p.drawImage(settings.STATIC_ROOT + "/img/entete.PNG",
                14 * cm, 27.5 * cm, width=15 * cm, height=2.5 * cm, mask="auto")
    p.setFont("Times-Italic", 0.5 * cm)
    if is_enfant:
        p.drawString(18 * cm, 29 * cm, "CHATON")
    else:
        p.drawString(18 * cm, 29 * cm, "ADULTE")
    # Titre
    style = ParagraphStyle(name="Style", textColor=couleur_ronrhone, fontSize=0.8 * cm, borderWidth=2, \
                           borderColor=couleur_ronrhone,
                           borderRadius=0.2 * cm,
                           borderPadding=(0.2 * cm, 0.5 * cm, 1.5 * cm, 0.5 * cm))

    para = Paragraph("{} <br/><br/> {} <br/>" \
                     .format("Contrat d'adoption de ", animal.nom)
                     , style=style)
    para.wrap(8 * cm, 7 * cm)
    para.drawOn(p, 8.5 * cm, 26 * cm)


def infos_personnelles(p, animal):
    # Informations personnelles de l'adoptant

    para = Paragraph("{} <br/>" \
                     .format("Informations personnelles de l'adoptant")
                     , style=titleStyle)
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
    p.drawString(3 * cm, 16.3 * cm, "Je m'engage à transmettre ce contrat d'adoption à la Fondation Capellino,")
    p.drawString(2 * cm, 15.65 * cm, "afin de permettre à l'Association Ron'Rhône d'obtenir le don associé,")
    p.drawString(2 * cm, 15.0 * cm, "sur ce lien https://pages.almonature.com/fr/adopt-me-europe ")
    p.drawString(2 * cm, 14.35 * cm, "Si je ne souhaite pas transmettre les coordonnées, ")
    p.drawString(2 * cm, 13.7 * cm, "je m'engage à envoyer ce contrat en masquant celles-ci.")


def infos_pensionnaire(p, animal, is_enfant):
    para = Paragraph("{} <br/>" \
                     .format("Informations sur le pensionnaire adopté")
                     , style=titleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, 12.5 * cm)

    p.setFont("Helvetica", 0.5 * cm)
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


def info_tarifs_chatons(p, animal):
    if animal.vaccin_ok == OuiNonChoice.OUI.name:
        vaccination = "- Vaccination à jour"
    else:
        vaccination = "- Primo vaccination"
    if animal.sterilise == OuiNonChoice.OUI.name:
        sterilise = "- Stérilisation"
    else:
        sterilise = ""
    elements = [["Les frais d'adoption sont de " + str(animal.get_latest_adoption().montant) + " euros.", ''],
                ["(majoration de ", '20€ pour une primo-vaccination leucose,'],
                ["", '40€ pour une vaccination leucose à jour).'],
                ["Cette somme correspond au remboursement des frais vétérinaires", ''],
                ["qui incluent les prestations suivantes : ", ''],
                ["", '- Identification par puce électronique'],
                ["", '- Test FIV / FeLV'],
                ["", vaccination],
                ["", '- Anti-parasitaires'],
                ["", '- Certificat de bonne santé'],
                ["", sterilise]]
    tableau = Table(elements, colWidths=[2.75 * cm, 14.25 * cm])
    # part de en haut à gauche !
    # tableau pour faire le cadre mais également la séparation avant la somme des vaccinations
    tableau.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, - 1), 0.75, colors.black),
        ('BOX', (1, 1), (-2, -9), 0.75, colors.black),
    ]))

    tableau.wrap(18 * cm, 20 * cm)
    tableau.drawOn(p, 2 * cm, 1.5 * cm)


def info_tarifs_adulte(p):
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


def info_rappel_vaccin(p, animal):
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
        else:
            prochain_vaccin = animal.date_dernier_vaccin + relativedelta(months=1)
        prochain_vaccin_str = prochain_vaccin.strftime("%d/%m/%Y")
    else:
        prochain_vaccin = None
        prochain_vaccin_str = "__/__/__"
    if animal.vaccin_ok == OuiNonChoice.OUI.name:
        p.drawString(5.5 * cm, 27.5 * cm, "peu de temps avant le " +
                     prochain_vaccin_str + ".")
    elif prochain_vaccin:
        vaccin_delai = prochain_vaccin + relativedelta(days=7)
        p.drawString(5.5 * cm, 27.5 * cm, "entre le " + prochain_vaccin_str +
                     " et le " + vaccin_delai.strftime("%d/%m/%Y") + ".")
    # On ne peut pas faire autrement qu'avec les paragraphes pour souligner du texte optimalement
    para = Paragraph("<font face='times-bold' size=14><u> {} </u></font> <br/>" \
                     .format("Attention, ce rappel sera à votre charge !"))
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 3.75 * cm, 26.3 * cm)


def info_sterilisation(p, spaceStyle, animal):
    p.circle(3.5 * cm, 25.45 * cm, 2.5, fill=True)
    para = Paragraph("<font face='helvetica' size=12> {} </font> \
                <font face='times-bolditalic' size=14><u> {} </u></font> <br/> \
                <font face='helvetica' size=12> {} </font>" \
                     .format("La stérilisation du chaton devra être effectuée ", "OBLIGATOIREMENT",
                             "avant ses 7 mois, soit :"))
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


def exigences_alimentaires(p, animal, vertical):
    para = Paragraph("{} <br/>" \
                     .format("Exigences alimentaires")
                     , style=titleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, vertical * cm)

    para = Paragraph("Le chat susnommé " + animal.nom + " devra être nourri avec une alimentation répondant"
                                " aux dernières recommandations. Soit, conformément aux taux analytiques "
                                "inscrits dans les annexes 1 et 2, les aliments de supermarché étant "
                                                        "proscrits.", style=blackParagraphStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 1.5 * cm, (vertical - 2.25) * cm)

    para = Paragraph("Si l'association, lors de la visite de \
                            postadoption, atteste que l'alimentation ne suit pas ces recommandations, le\
                            chat pourra être, le cas échéant, récupéré par l'Association sans remboursement "
                     "des frais d'adoption.", style=redParagraphStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 1.5 * cm, (vertical - 3.75) * cm)


def engagement(p, animal, vertical):
    para = Paragraph("{} <br/>".format("Engagement"), style=titleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, vertical * cm)

    para = Paragraph("Je soussigné(e) " + animal.get_latest_adoption().adoptant.nom +
                     " " + animal.get_latest_adoption().adoptant.prenom +
                     " certifie l’exactitude des informations renseignées "
                     "sur ce contrat et m’engage à respecter la charte jointe à ce dernier. "
                     "Le non-respect de ce contrat, et/ou de la charte fournie avec celui-ci "
                     "entraîne sa résiliatioet ainsi la restitution immédiate du chat à "
                     "l’association Ron’Rhône, sans remboursementdes frais d’adoption.", style=blackParagraphStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 1.5 * cm, (vertical-3.5) * cm)

    date_id = timezone.now().date() + relativedelta(months=2)
    para = Paragraph("L’identification au nom du nouveau propriétaire sera établie "
                     "après réception du certificat de stérilisation, de la visite, "
                     "ainsi que les rappels de vaccins, soit aux alentours du "
                     + date_id.strftime("%d/%m/%Y") +".", style=blackParagraphStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 1.5 * cm, (vertical - 5) * cm)


    p.setFillColor("red")
    p.drawString(1.5 * cm, (vertical - 6) * cm, "ATTENTION ! AUCUN CHAT NE DOIT AVOIR ACCES"
                                                  " A UN ESPACE")
    p.drawString(1.5 * cm, (vertical - 6.7) * cm, "EXTERIEUR AVANT SA STERILISATION.")

    para = Paragraph("Dans cette même période, l’Association et le nouveau propriétaire "
                     "devront entretenir un rapport régulier pour s’assurer du bien-être de "
                     "l’animal dans son nouvel habitat.", style=blackParagraphStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 1.5 * cm, (vertical - 8.5) * cm)

    para = Paragraph("Nous vous rappelons que nous restons à votre disposition "
                     "pour toutes questions concernant le chat avant et après l’adoption.",
                     style=blackParagraphStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 1.5 * cm, (vertical - 9.5) * cm)

    para = Paragraph("Vous pourrez récupérer " + animal.nom +
                     " dès validation de l’adoption et réception du paiement par l’Association."
                     "Organisez-vous avec la famille d'accueil pour récupérer votre nouveau compagnon. <br/>"
                     "<br/> Visite dans 2 mois pour valider l’adoption (nous prévenir si vous voulez changer son nom).",
                     style=blueParagraphStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 1.5 * cm, (vertical - 12.5) * cm)



def montants(p, animal, vertical):
    p.drawImage(settings.STATIC_ROOT + "/img/montants.PNG",
                1.5 * cm, vertical * cm, width=18 * cm, height=6 * cm, mask="auto")
    try:
        bon = animal.get_latest_adoption().bon
    except Adoption._meta.model.bon.RelatedObjectDoesNotExist :
        bon = None
    montant_bon = None
    if bon:
        if animal.sexe == SexeChoice.F.name:
            montant_bon = Decimal(80)
        else:
            montant_bon = Decimal(45)

    p.setFont("Helvetica", 0.3 * cm)
    p.setFillColor("black")
    if montant_bon:
        p.drawString(9.4 * cm, (vertical + 4.5) * cm, str(animal.get_latest_adoption().montant -
                                                          montant_bon))
    else:
        p.drawString(9.4 * cm, (vertical + 4.5) * cm, str(animal.get_latest_adoption().montant))

    if animal.get_latest_adoption().montant_restant:
        montant_restant = animal.get_latest_adoption().montant_restant
    elif animal.get_latest_adoption().montant:
        montant_restant = animal.get_latest_adoption().montant/2
    else:
        montant_restant = Decimal(0)
    if animal.get_latest_adoption().montant:
        p.drawString(9.4 * cm, (vertical + 3.8) * cm, str(animal.get_latest_adoption().montant -
                                                      montant_restant))
    if montant_bon:
        p.drawString(9.4 * cm, (vertical + 3.1) * cm, str(montant_bon))


def signatures(p, vertical):
    p.drawImage(settings.STATIC_ROOT + "/img/signatures.PNG",
                1.5 * cm, vertical * cm, width=16 * cm, height=4.5 * cm, mask="auto")