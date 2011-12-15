tinyMCE.init({
	mode : "textareas",
	editor_deselector : "noMCE",
	theme : "advanced",
	content_css : "/media/static/css/general.css",
	gecko_spellcheck : true,
	width : "600",
	height: "300",
	convert_urls : false,
	theme_advanced_toolbar_location : "top",
	theme_advanced_toolbar_align : "left",
	theme_advanced_buttons1 : "formatselect,bold,italic,underline,separator,bullist,numlist,outdent,indent,|,charmap,|,link,unlink,|,undo,redo,|,removeformat,cleanup,code",
	theme_advanced_buttons2 : "pastetext,pasteword,selectall,|,tablecontrols,|,anchor,image",
	theme_advanced_buttons3 : "",
	theme_advanced_blockformats : "",
	auto_cleanup_word : true,
	plugins : "table,iespell,searchreplace,contextmenu,paste",
	theme_advanced_blockformats : "h2,h3,h4,h5",
	paste_auto_cleanup_on_paste : true,
	extended_valid_elements : "a[name|href|target=_self|title|onclick],img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name],hr[class|width|size|noshade],font[face|size|color|style],span[class|align|style],form[action|method],input[type|name|value|src|border]"
});
