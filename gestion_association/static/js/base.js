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