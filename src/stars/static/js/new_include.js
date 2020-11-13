function expandCollapse(image, expandOnly) {
    id = image.id;
    obj = document.getElementById(id + "_target");
    if( obj != null ) {
        if( obj.style.display == "none" || expandOnly) {
            obj.style.display = "block";
            image.src = '/media/static/images/collapse_big.gif';
            image.alt = "-";
        }
        else {
            obj.style.display = "none";
            image.src = '/media/static/images/expand_big.gif';
            image.alt = '+';
        }
    }
}

function jumpToSubcat(cat_id, sub_id) {
    // 1 Expand Category
    // 2 Expand Subcategory
    // 3 Jump to bookmark

    jump = "ec_" + cat_id;
    cat_img = document.getElementById(jump);
    expandCollapse(cat_img, true);
    if( sub_id ) {
    	jump = "ec_" + cat_id + "_" + sub_id;
    	sub_img = document.getElementById(jump);
    	expandCollapse(sub_img, true);
    }
    document.location = "#" + jump;
    return false;
}

function collapseSummary() {
    /**
        Collapses the summary outline but leaves a subcategory and category
        open if an anchor has been used

        Anchors will be in the format "ec_<cat_id>" and "ec_<cat_id>_<sub_id>"
    **/

    // Parse Anchor
    anchor = self.document.location.hash;
    cat = null;
    sub = null;
    if( anchor ) {
        if( anchor.match(/ec_\d+/) ) {
            cat = anchor.split('_')[1];
        }
        if( anchor.match(/ec_\d+_\d+/) ) {
            cat = anchor.split('_')[1];
            sub = anchor.split('_')[2];
        }
    }
    images = document.getElementsByTagName('IMG');
    for(var i = 0; i < images.length; i++) {
    	css_class = images[i].className
        if(	images[i].id.match("ec_.*") &&
        	images[i].id != "ec_" + cat &&
        	images[i].id != "ec_" + cat + "_" + sub &&
        	css_class.search(/initial_expand/g) == -1
        ) {
            expandCollapse(images[i], false);
        }
    }
}

function disable_select_options() {
    /**
        Disable any options in select inputs that have a value of -1
    **/
    options = document.getElementsByTagName('option');
    count = 0
    for(var i = 0; i < options.length; i++) {
        if(options[i].value == '-1')
            options[i].disabled = 'disabled';
            count++;
    }
}

function addFormToFormset(prefix) {

    total_forms = $('#id_' + prefix + '-TOTAL_FORMS').val();

    // Clone the chosen table
    table_selector = "#" + prefix + "_table" + (total_forms-1)
    var clone = $(table_selector).clone(true);

    // Get the new id
    total_forms++;
    clone.attr({'id': prefix + "_table" + (total_forms-1)});
    if( total_forms % 2 == 0 )
        clone.attr({'style': "background-color: #ddd"});
    else
        clone.attr({'style': "background-color: inherit"});

    if (total_forms > 1 ) {
        // Update inputs
        search_string = prefix + "-" + (total_forms - 2) + "-";
        replace_string = prefix + "-" + (total_forms - 1) + "-";

        clone.find(':input').each(function() {
            var name = $(this).attr('name').replace(search_string, replace_string);
            var id = $(this).attr('id').replace("id_" + search_string, "id_" + replace_string);
            $(this).attr({'name': name, 'id': id}).val('').removeAttr('checked');
        });

        clone.find('label').each(function() {
            var id = $(this).attr('for').replace("id_" + search_string, "id_" + replace_string);
            $(this).attr({'id': id});
        });

        clone.find('select').each(function() {
            var name = $(this).attr('name').replace(search_string, replace_string);
            var id = $(this).attr('id').replace("id_" + search_string, "id_" + replace_string);
            $(this).attr({'name': name, 'id': id, 'selectedIndex': 0});
        });

        // Remove any errors
        clone.find('ul').each(function() {
            if( $(this).attr('class') == "errorlist" )
                $(this).remove();
        });
    }

    $(table_selector).after(clone);
    $('#id_' + prefix + '-TOTAL_FORMS').val(total_forms);
}
