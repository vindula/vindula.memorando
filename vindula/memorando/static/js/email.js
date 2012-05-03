$j = jQuery.noConflict();

function checkValue(val){
	alert(val);
	if (val == 'usuario_fora_intranet') {
		$j('#archetypes-fieldname-email_to').fadeIn('slow');
	}
	else {
		$j('#archetypes-fieldname-email_to').fadeOut('slow');
		};
	};


$j(document).ready(function(){
	var val = $j('#email_to').val();
	checkValue(val);
	$j('#to').change(function(evt){
		var val = $j('#email_to').val();
		checkValue(val);
	});	

});