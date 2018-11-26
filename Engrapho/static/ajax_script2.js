$(document).ready(function() {
	$('form').on('submit', function(event) {
		$.ajax({
			data : {
				search: $('#search').val()
			},
			type: 'POST',
			url: '/search'
		})
		.done(function(data) {
			console.log(data)
			/*if(data.error) {
				$('#errorAlert').text(data.error).show();
				$('#sucessAlert').hide();
			}
			else {
				$('#errorAlert').hide();
				#('#successAlert').text(data.name).show();
			}*/
		})
		event.preventDefault();
	})
})