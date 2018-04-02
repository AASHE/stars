$(document).ready(function(){

	$('a').click(function(e){

    e.preventDefault();
    var thisHref = $(this).attr('href');
    if($('#data-changed').hasClass("form-has-changed")){
			$("#id_submission_status").val('p');
      $('#unsaved-data').modal();
      $('.modal-close-button').click(function(){
        window.location.href = thisHref;
      });
			$('.modal-stash-changes').click(function(){
				$('#myModalLabel').html("One moment...");
				$('.modal-footer').hide();
				$('#modal-p').hide();
				$('.spinner').slideDown();
        var frm = $('.submit_form');
        //fill in this ajax
				$.ajax({
            type: frm.attr('method'),
            url: frm.attr('action'),
            data: frm.serialize(),
            success: function (data) {
								window.location.href = thisHref;
            },
            error: function(data) {
                $("#modal-p").html("Something went wrong!");
            }
        });

			});
    }
    else{
      window.location.href = thisHref;
    }

	});

});
