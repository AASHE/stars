var MIN_LETTERS_SEARCH = 4;

function search_institution(input) {
    
    if(input.value.length >= MIN_LETTERS_SEARCH) {
        // Only run the search if there are at least three characters already
    
        // Filter out non-alpha-numeric, excpet allow blanks and dashes (-)
        // Ideally, this filter is the opposite of the URL pattern for the gateway - see ticket #220
        value = input.value.replace(/[^\d\w\-\. ]+/g, '')
        url = "/tool/admin/gateway/find-institution/";
        url += value;
        search(url);
    }
    
}

function search(url) {
    target = document.getElementById('search_target');
    target.innerHTML = "<p align='center'>Loading<br/><img src='/media/static/images/loading_long_bar.gif' alt='...'/></p>";
    ajaxQuery(url, target);
}

function delete_file(elementId, filename, url) {
    if( confirm("Are you sure you want to delete " + filename) ) {
        target = document.getElementById(elementId);
        ajaxQuery(url, target)
    }
}

function ajaxQuery(url, target)
{ 
    var xhr; 
    try {  xhr = new ActiveXObject('Msxml2.XMLHTTP');   }
    catch (e) 
    {
        try {   xhr = new ActiveXObject('Microsoft.XMLHTTP');    }
        catch (e2) 
        {
            try {  xhr = new XMLHttpRequest();     }
            catch (e3) {  xhr = false;   }
        }
    }

    xhr.onreadystatechange  = function()
    { 
        if(xhr.readyState  == 4)
        {
            if(xhr.status  == 200) 
                target.innerHTML = xhr.responseText; 
            else if(xhr.status == 403)
                target.innerHTML = "Permission Denied."
            else
                target.innerHTML = "Connection failed. Please try again later. <!-- Error code: " + xhr.status + "-->";
        }
    }; 

    xhr.open("POST", url, true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.send(null);
} 

function ajaxGetQuery(url, target) {
	
	var xmlhttp;
	if (window.XMLHttpRequest) {// code for IE7+, Firefox, Chrome, Opera, Safari
		xmlhttp = new XMLHttpRequest();
	}
	else {// code for IE6, IE5
		xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
	}
	xmlhttp.onreadystatechange = function() {
		if (xmlhttp.readyState==4 && xmlhttp.status==200) {
	    	target.innerHTML = xmlhttp.responseText;
	    }
	}
	xmlhttp.open("GET", url, true);
    //xmlhttp.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
	xmlhttp.send();
}
