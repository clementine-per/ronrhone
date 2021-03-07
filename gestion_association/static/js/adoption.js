$(function() {
  $('[name="date"],[name="date_visite"]').datepicker({
      dateFormat: 'dd/mm/yy'
  });
});

$('#adoptionForm').on('change', '*', function(event) {
    var champs_restant = ['acompte_verse','montant','show'];
    var champ_sterilisation = ['show'];
    if (champs_restant.indexOf(event.target.name)!=-1){
        var url = $("#adoptionForm").data("calcul-montant-url");
        $.post(url,$('#adoptionForm').serialize(),function (data){
            $("#id_montant").val(data["montant"]);
            $("#id_montant_restant").val(data["montant_restant"]);
        });
    }
    if (champ_sterilisation.indexOf(event.target.name)!=-1){
        var url = $("#adoptionForm").data("calcul-montant-sterilisation-url");
        $.post(url,$('#adoptionForm').serialize(),function (data){
            $("#id_montant").val(data["montant"]);
            $("#id_montant_restant").val(data["montant_restant"]);
        });
    }
 });

document.addEventListener("DOMContentLoaded", function() {
    var value = $('select#id_show').val();

    var fields = $('input[name="date_max"], input[name="date_utilisation"],\
					select[name="envoye"], select[name="utilise"],\
					label[for="id_envoye"], label[for="id_utilise"],\
					label[for="id_date_max"], label[for="id_date_utilisation"]')
    switch(value) {
		case "OUI":
			fields.show()
			break;
		case "NON":
			fields.hide()
			break;
	}
});

$('select#id_show').change(function(){
	var value = $(this).val();
	var fields = $('input[name="date_max"], input[name="date_utilisation"],\
					select[name="envoye"], select[name="utilise"],\
					label[for="id_envoye"], label[for="id_utilise"],\
					label[for="id_date_max"], label[for="id_date_utilisation"]')
	switch(value) {
		case "OUI":
			fields.show()
			break;
		case "NON":
			fields.hide()
			break;
	}

 });