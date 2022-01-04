$(function () {
  $('.datePicker').datepicker({
    dateFormat: "dd/mm/yy",
    firstDay: 1,
    monthNames: ['Janvier','Fevrier','Mars','Avril','Mai','Juin',
		'Juillet','Aout','Septembre','Octobre','Novembre','Decembre'],
		monthNamesShort: ['Jan','Fev','Mar','Avr','Mai','Jun',
		'Jul','Aou','Sep','Oct','Nov','Dec'],
	dayNamesMin: ['Di','Lu','Ma','Me','Je','Ve','Sa'],
  });
});

function selectAllStatuts(select_id)
{
    selectBox = document.getElementById(select_id);
    for (var i = 0; i < selectBox.options.length; i++) {
         selectBox.options[i].selected = true;
    }

}
function unSelectAllStatuts(select_id)
{
    selectBox = document.getElementById(select_id);
    for (var i = 0; i < selectBox.options.length; i++) {
         selectBox.options[i].selected = false;
    }

}