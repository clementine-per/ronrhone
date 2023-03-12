import io
import tempfile
from decimal import Decimal

import PyPDF2
from django.utils import timezone
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, TableStyle
from dateutil.relativedelta import relativedelta

from gestion_association.models import OuiNonChoice
from gestion_association.models.adoption import Adoption
from gestion_association.models.animal import SexeChoice, TrancheAge
from django.conf import settings

# Styles and colors for generating the contract
ronrhone_color = '#00bfff'
blackParagraphStyle = ParagraphStyle(name="Black", textColor="black", alignement=TA_JUSTIFY, fontSize=0.5 * cm,
                                     fontName="Helvetica", borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))
redParagraphStyle = ParagraphStyle(name="Red", textColor="red", alignement=TA_JUSTIFY, fontSize=0.5 * cm,
                                   fontName="Helvetica", borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))
blueParagraphStyle = ParagraphStyle(name="Blue", textColor=ronrhone_color, alignement=TA_JUSTIFY, fontSize=0.5 * cm,
                                    fontName="Helvetica", borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))
# Style for paragraphs
spaceStyle = ParagraphStyle(name='spaceStyle', leading=17)
# Style for subtitles
subtitleStyle = ParagraphStyle(name="Style", textColor=ronrhone_color, fontSize=0.7 * cm, borderWidth=1,
                               borderColor=ronrhone_color,
                               # top , right, bottom, left
                               borderPadding=(0.01 * cm, 1 * cm, 0.5 * cm, 2.7 * cm))
titleStyle = ParagraphStyle(name="Style", textColor=ronrhone_color, fontSize=0.8 * cm, borderWidth=2,
                            borderColor=ronrhone_color,
                            borderRadius=0.2 * cm,
                            borderPadding=(0.2 * cm, 0.5 * cm, 1.5 * cm, 0.5 * cm))


def next_page(p, nb_page):
    # page footer
    page_footer(p, nb_page)
    # Go to next page
    p.showPage()
    return nb_page + 1


def get_data_certified_engagement(animal):
    result_bytes = io.BytesIO()
    certificate_canvas = canvas.Canvas(result_bytes)
    certificate_canvas.setFont("Helvetica", 0.4 * cm)
    certificate_canvas.drawString(3.6 * cm, 24 * cm, animal.adoptant.prenom)
    certificate_canvas.drawString(3.4 * cm, 23.5 * cm, animal.adoptant.nom)
    certificate_canvas.drawString(3.5 * cm, 23 * cm, animal.adoptant.adresse)
    certificate_canvas.drawString(2 * cm, 22.45 * cm, animal.adoptant.code_postal + " " + animal.adoptant.ville)
    certificate_canvas.drawString(3.5 * cm, 21.9 * cm, animal.adoptant.email)
    certificate_canvas.save()
    result_bytes.seek(0)
    return result_bytes


def contract_pieces(p, vertical):
    para = Paragraph("{} <br/>" \
                     .format("Pièces à joindre au contrat")
                     , style=subtitleStyle)
    para.wrap(13 * cm, 15 * cm)
    para.drawOn(p, 4.5 * cm, vertical * cm)
    p.setFont("Helvetica", 0.5 * cm)
    p.drawString(2 * cm, (vertical - 1.2) * cm, "✓ Photocopie de votre pièce d'identité")
    p.drawString(2 * cm, (vertical - 1.7) * cm, "✓ Photocopie d'un justificatif de domicile de moins de 3 mois")


def page_footer(p, nb_page):
    p.setFont("Times-Italic", 0.35 * cm)
    p.setFillColor('#808080')
    p.drawString(2.7 * cm, 0.2 * cm,
                 "Association Ron’Rhône - 98, chemin de la Combe Moussin 38270 BEAUFORT - n° SIRET : 82140540400012")
    p.setFont("Times-Bold", 0.5 * cm)
    p.setFillColor('#000000')
    p.drawString(20 * cm, 0.2 * cm, str(nb_page) + "/9")


def generation_payment(p, difference, animal):
    para = Paragraph("{} <br/>" \
                     .format("Règlement")
                     , style=subtitleStyle)
    para.wrap(7 * cm, 15 * cm)
    para.drawOn(p, 4.5 * cm, 17 * cm + difference * cm)
    p.circle(2.5 * cm, 15.4 * cm + difference * cm, 2.5, fill=True)
    para = Paragraph("<font face='times-bold' size=14><u>Paylib ou Lydia :</u>  </font><br/> \
                        <font face='helvetica-oblique' size=14 color='#2d8dfd'>06. 64. 62. 32. 07.</font>",
                     style=spaceStyle)
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
                     , style=spaceStyle)
    para.wrap(17 * cm, 15 * cm)
    para.drawOn(p, 2.25 * cm, 9.5 * cm + difference * cm)
    p.drawImage(settings.STATIC_ROOT + "/img/RIB.PNG",
                0.75 * cm, 1 * cm + difference * cm, width=19.5 * cm, height=8 * cm, mask="auto")


def header(p, animal):
    # logo header
    p.drawImage(settings.STATIC_ROOT + "/img/logo.PNG",
                0.75 * cm, 23.25 * cm, width=5.5 * cm, height=5.5 * cm, mask="auto")
    # Type of contract, top right
    p.drawImage(settings.STATIC_ROOT + "/img/entete.PNG",
                14 * cm, 27.5 * cm, width=15 * cm, height=2.5 * cm, mask="auto")
    p.setFont("Times-Italic", 0.5 * cm)
    if animal.tranche_age == TrancheAge.ENFANT.name:
        p.drawString(18 * cm, 29 * cm, "CHATON")
    else:
        p.drawString(18 * cm, 29 * cm, "ADULTE")

    para = Paragraph("{} <br/><br/> {} <br/>" \
                     .format("Contrat d'adoption de ", animal.nom)
                     , style=titleStyle)
    para.wrap(8 * cm, 7 * cm)
    para.drawOn(p, 8.5 * cm, 26 * cm)


def personal_infos(p, animal):
    # Personal information of the person adopting

    para = Paragraph("{} <br/>" \
                     .format("Informations personnelles de l'adoptant")
                     , style=subtitleStyle)
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


def infos_animal(p, animal):
    para = Paragraph("{} <br/>" \
                     .format("Informations sur le pensionnaire adopté")
                     , style=subtitleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, 12.5 * cm)

    p.setFont("Helvetica", 0.5 * cm)
    p.drawString(2 * cm, 11.35 * cm, "- Identification : " + animal.identification)
    p.drawString(11 * cm, 11.35 * cm, "- Test FeLV : " + animal.felv)
    if animal.tranche_age == TrancheAge.ENFANT.name:
        p.drawString(2 * cm, 10.75 * cm, "- Nom du chaton : " + animal.nom)
    else:
        p.drawString(2 * cm, 10.75 * cm, "- Nom du chat : " + animal.nom)
    p.drawString(11 * cm, 10.75 * cm, "- Test FIV : " + animal.fiv)
    p.drawString(2 * cm, 10.15 * cm, "- Sexe : " + animal.sexe)
    p.drawString(11 * cm, 10.15 * cm, "- Race : " + animal.type)
    if animal.date_naissance:
        p.drawString(2 * cm, 9.55 * cm, "- Date de naissance : " + animal.date_naissance.strftime("%d/%m/%Y"))
    p.drawString(11 * cm, 9.55 * cm, "- Robe : ")
    p.drawString(2 * cm, 8.95 * cm, "- Signes particuliers : ")


def info_prices(p, animal):
    if animal.tranche_age == TrancheAge.ENFANT.name:
        info_prices_child(p, animal)
    else:
        info_prices_adult(p)


def info_prices_child(p, animal):
    if animal.vaccin_ok == OuiNonChoice.OUI.name:
        vaccination = "- Vaccination à jour"
    else:
        vaccination = "- Primo vaccination"
    if animal.sterilise == OuiNonChoice.OUI.name:
        sterilisation = "- Stérilisation"
    else:
        sterilisation = ""
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
                ["", sterilisation]]
    table = Table(elements, colWidths=[2.75 * cm, 14.25 * cm])
    # Starts top left !
    # table to do the border but also seperate before vaccination prices
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, - 1), 0.75, colors.black),
        ('BOX', (1, 1), (-2, -9), 0.75, colors.black),
    ]))

    table.wrap(18 * cm, 20 * cm)
    table.drawOn(p, 2 * cm, 1.5 * cm)


def info_prices_adult(p):
    elements = [[Paragraph("Chat femelle Primo"),
                 Paragraph("Identification + Stérilisation + Primo vaccin + Test FIV/FELV + Déparasitant + Vermifuge"),
                 "170€"],
                [Paragraph("Chat femelle Primo + Rappel"), Paragraph(
                    "Identification + Stérilisation + Vaccins à jour + Test FIV/FELV + Déparasitant + Vermifuge"),
                 "200€"],
                [Paragraph("Chat mâle Primo"),
                 Paragraph("Identification + Castration + Primo vaccin + Test FIV/FELV + Déparasitant + Vermifuge"),
                 "150€"],
                [Paragraph("Chat mâle Primo + Rappel"),
                 Paragraph("Identification + Castration + Vaccins à jour + Test FIV/FELV + Déparasitant + Vermifuge"),
                 "180€"]]
    table = Table(elements, colWidths=[3 * cm, 12 * cm, 2 * cm])
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, - 1), 0.75, colors.black),
        ('INNERGRID', (0, 0), (-1, - 1), 0.75, colors.black),
    ]))

    table.wrap(18 * cm, 20 * cm)
    table.drawOn(p, 2 * cm, 4 * cm)

    elements = [["(majoration de ", '20€ pour une primo-vaccination leucose,'],
                ["", '40€ pour une vaccination leucose à jour).']]
    table = Table(elements, colWidths=[2.75 * cm, 14.25 * cm])
    # Starts top left !
    # table to do the border but also seperate before vaccination prices
    # Draw border in black and then erase some part with white on top
    table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, - 1), 0.75, colors.white),
        ('BOX', (1, 0), (-2, -1), 0.75, colors.black),
    ]))

    table.wrap(18 * cm, 20 * cm)
    table.drawOn(p, 2 * cm, 2.5 * cm)


def info_vaccine_shot(p, animal):
    # Bullet point start of paragraph
    p.circle(3.5 * cm, 28.55 * cm, 2.5, fill=True)
    p.drawString(4 * cm, 28.4 * cm, "Le prochain rappel de vaccin de " + animal.nom + " est à faire :")
    # Calculate next vaccine shot date
    if animal.date_prochain_vaccin:
        next_vaccine = animal.date_prochain_vaccin
        next_vaccine_str = next_vaccine.strftime("%d/%m/%Y")
    elif animal.date_dernier_vaccin:
        if animal.vaccin_ok == OuiNonChoice.OUI.name:
            next_vaccine = animal.date_dernier_vaccin + relativedelta(years=1)
        else:
            next_vaccine = animal.date_dernier_vaccin + relativedelta(months=1)
        next_vaccine_str = next_vaccine.strftime("%d/%m/%Y")
    else:
        next_vaccine = None
        next_vaccine_str = "__/__/__"
    if animal.vaccin_ok == OuiNonChoice.OUI.name:
        p.drawString(5.5 * cm, 27.5 * cm, "peu de temps avant le " +
                     next_vaccine_str + ".")
    elif next_vaccine:
        next_vaccine_delay = next_vaccine + relativedelta(days=7)
        p.drawString(5.5 * cm, 27.5 * cm, "entre le " + next_vaccine_str +
                     " et le " + next_vaccine_delay.strftime("%d/%m/%Y") + ".")
    else:
        p.drawString(5.5 * cm, 27.5 * cm, "peu de temps avant le " +
                     next_vaccine_str + ".")
    # Use Paragraph style to underline text
    para = Paragraph("<font face='times-bold' size=14><u> {} </u></font> <br/>" \
                     .format("Attention, ce rappel sera à votre charge !"))
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 3.75 * cm, 26.3 * cm)


def info_sterilisation(p, animal):
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
    para = Paragraph("<font face='helvetica' size=12>Si l’Association ne reçoit pas de certificat de stérilisation "
                     "avant <br/> \ l’anniversaire des 7 mois du chaton, soit le {}, elle se réserve le<br/> \ droit "
                     "de récupérer le chaton sans remboursement d’aucun frais engagé \ par l’adoptant et d’encaisser "
                     "le chèque de caution éventuel</font>"
                     .format((animal.date_naissance + relativedelta(months=7)).strftime("%d/%m/%Y")))
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4 * cm, 20 * cm)
    p.circle(3.5 * cm, 19 * cm, 2.5, fill=True)
    para = Paragraph("<font face='helvetica' size=12>Environ deux mois après l’adoption, l’Association prendra "
                     "rendez-vous <br/> \ avec vous pour une visite de contrôle, effectuée par un membre de <br/> \ "
                     "l’Association. </font>")
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4 * cm, 18 * cm)


def food_info(p, animal, vertical):
    para = Paragraph("{} <br/>"
                     .format("Exigences alimentaires")
                     , style=subtitleStyle)
    para.wrap(14 * cm, 15 * cm)
    para.drawOn(p, 4.30 * cm, vertical * cm)

    para = Paragraph("Le chat susnommé " + animal.nom + " devra être nourri avec une alimentation répondant"
                                                        "aux dernières recommandations. Soit, conformément aux taux "
                                                        "analytiques "
                                                        "inscrits dans les annexes 1 et 2, les aliments de "
                                                        "supermarché étant "
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
    para = Paragraph("{} <br/>".format("Engagement"), style=subtitleStyle)
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
    para.drawOn(p, 1.5 * cm, (vertical - 3.5) * cm)

    date_id = timezone.now().date() + relativedelta(months=2)
    para = Paragraph("L’identification au nom du nouveau propriétaire sera établie "
                     "après réception du certificat de stérilisation, de la visite, "
                     "ainsi que les rappels de vaccins, soit aux alentours du "
                     + date_id.strftime("%d/%m/%Y") + ".", style=blackParagraphStyle)
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


def amounts(p, animal, vertical):
    p.drawImage(settings.STATIC_ROOT + "/img/montants.PNG",
                1.5 * cm, vertical * cm, width=18 * cm, height=6 * cm, mask="auto")
    try:
        coupon = animal.get_latest_adoption().bon
    except Adoption._meta.model.bon.RelatedObjectDoesNotExist:
        coupon = None
    amount_coupon = None
    if coupon:
        if animal.sexe == SexeChoice.F.name:
            amount_coupon = Decimal(80)
        else:
            amount_coupon = Decimal(45)

    p.setFont("Helvetica", 0.3 * cm)
    p.setFillColor("black")
    if amount_coupon:
        p.drawString(9.4 * cm, (vertical + 4.5) * cm, str(animal.get_latest_adoption().montant -
                                                          amount_coupon))
    else:
        p.drawString(9.4 * cm, (vertical + 4.5) * cm, str(animal.get_latest_adoption().montant))

    if animal.get_latest_adoption().montant_restant:
        remaining_amount = animal.get_latest_adoption().montant_restant
    elif animal.get_latest_adoption().montant:
        remaining_amount = animal.get_latest_adoption().montant / 2
    else:
        remaining_amount = Decimal(0)
    if animal.get_latest_adoption().montant:
        p.drawString(9.4 * cm, (vertical + 3.8) * cm, str(animal.get_latest_adoption().montant -
                                                          remaining_amount))
    if amount_coupon:
        p.drawString(9.4 * cm, (vertical + 3.1) * cm, str(amount_coupon))


def signatures(p, vertical):
    p.drawImage(settings.STATIC_ROOT + "/img/signatures.PNG",
                1.5 * cm, vertical * cm, width=16 * cm, height=4.5 * cm, mask="auto")


def create_complete_pdf(temp_file, animal):
    # Merge between generated part and fixed part to add
    if animal.tranche_age == TrancheAge.ENFANT.name:
        fixed_contract = open(settings.STATIC_ROOT + "/pdf/contrat_chaton.pdf", 'rb')
    else:
        fixed_contract = open(settings.STATIC_ROOT + "/pdf/contrat_adulte.pdf", 'rb')
    certificat_engagement = open(settings.STATIC_ROOT + "/pdf/certificat-engagement.pdf", 'rb')
    # Temporary file containing the whole content
    pdf1_reader = PyPDF2.PdfFileReader(temp_file)
    pdf2_reader = PyPDF2.PdfFileReader(fixed_contract)
    certificat_engagement_data = get_data_certified_engagement(animal)
    pdf3_reader = PyPDF2.PdfFileReader(certificat_engagement)
    pdf_writer = PyPDF2.PdfFileWriter()
    for page in range(pdf1_reader.numPages):
        page_object = pdf1_reader.getPage(page)
        pdf_writer.addPage(page_object)
    for page in range(pdf2_reader.numPages):
        page_object = pdf2_reader.getPage(page)
        pdf_writer.addPage(page_object)
    for page in range(pdf3_reader.numPages):
        page_object = pdf3_reader.getPage(page)
        if page == 0:
            new_pdf = PyPDF2.PdfFileReader(certificat_engagement_data)
            page_object.mergePage(new_pdf.getPage(0))
        pdf_writer.addPage(page_object)
    pdf_output_file = tempfile.NamedTemporaryFile()
    pdf_writer.write(pdf_output_file)
    pdf_output_file.flush()
    pdf_output_file.seek(0)
    content = pdf_output_file.read()
    fixed_contract.close()
    pdf_output_file.close()

    return content
