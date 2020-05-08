$(document).ready(function(){
  
  $('#institution-selection').css("display","none");

  $('.org-list li').click(function(){
    var orgName = $(this).text();
    var orgID = $(this).attr("name");
    $('#institution-selection').css("display","block");
    $('#org-name').val(orgName);
    $('#asshe_id').val(orgID);
    $('.green-dot').show();
    hideList();
    clearSearch();
  });

  // $('#school-finder').focus(function(){
  // 
  // });

  $('#school-finder').on('keyup', debounce(function() {
    orgName = $(this).val();
    $('.org-list li').each(function(){
      if ($(this).text().search(new RegExp(orgName, 'i')) < 0){
        $(this).css("display","none");
      }
      else{
        $(this).css("display","block");
      }
    });
    showOrgs();
    $('.spinner').hide();
  }, 275));


});

function debounce(func, wait, immediate) {
  let timeout;
  return function() {
    $('.spinner').show();
	  let context = this, args = arguments;
	  const later = function() {
		  timeout = null;
			  if (!immediate) func.apply(context, args);
	  };
	  const callNow = immediate && !timeout;
	  clearTimeout(timeout);
	  timeout = setTimeout(later, wait);
	  if (callNow) func.apply(context, args);
  };
};


function showOrgs(){
  $('.org-list').slideDown();
}

function hideList(){
  $('.org-list').css("display","none");
}

function clearSearch(){
  $('#school-finder').val('');
}
