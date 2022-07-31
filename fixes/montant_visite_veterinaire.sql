select count(*), visitemedicale_id from gestion_association_visitemedicale_animaux group by visitemedicale_id;

select count(*), visitemedicale_id, montant, montant*count(*) as nouveau
from gestion_association_visitemedicale
join gestion_association_visitemedicale_animaux on
gestion_association_visitemedicale_animaux.visitemedicale_id = gestion_association_visitemedicale.id
group by visitemedicale_id, montant;

update gestion_association_visitemedicale 
join gestion_association_visitemedicale_animaux on
gestion_association_visitemedicale_animaux.visitemedicale_id = gestion_association_visitemedicale.id
set montant = montant*count(*)
group by visitemedicale_id, montant;