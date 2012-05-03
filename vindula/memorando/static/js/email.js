$j = jQuery.noConflict();

function checkValue(val){
	
	if (val == 'usuario_fora_intranet') {
		$j('#archetypes-fieldname-email_to').fadeIn('slow');
		$j('#email_to').val('');
	}
	else {
		$j('#archetypes-fieldname-email_to').fadeOut('slow');
		$j('#email_to').val(val);
		};
	};


$j(document).ready(function(){
	var val = $j('#to').val();
	checkValue(val);
	$j('#to').change(function(evt){
		var val = $j('#to').val();
		checkValue(val);
	});	

});