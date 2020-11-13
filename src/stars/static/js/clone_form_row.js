
var counter = 0  // ensure this gets zero'ed on every page load.

function cloneRow(count,table) {
    // Clone the first row of the table and replace the input element ids and names with new#, where # is count
	var rows=table.getElementsByTagName('tr');
	var clone=rows[rows.length-1].cloneNode(true);
	clone.className='new'
	// Inputs
	var inputs=clone.getElementsByTagName('input'), inp, i=0 ;
	while(inp=inputs[i++]){
        inp.id=inp.id.replace(/new\d+/g,'new'+counter);
		inp.name=inp.name.replace(/new\d+/g,'new'+counter);
		inp.value = ''
	}
	// Select
	//var inputs=clone.getElementsByTagName('select'), inp, i=0 ;
	//while(inp=inputs[i++]){
	//	inp.name=inp.name.replace(/\d/g,counter+1);
	//}
    return clone;
}

function addRow(counter_form, object_edit_table) {
    counter++;
	counter_form.counter.value = counter;
	
    var clone = cloneRow(counter, object_edit_table);
    var tbo=table.getElementsByTagName('tbody')[0];
    tbo.appendChild(clone);
}

function addObjectRow() {
    form = document.getElementById('object_editing_form');
    table = document.getElementById('object_editing_table');
    addRow(form, table)
}

function addChoice() {
    form = document.forms.documentationfield_form;
    table = document.getElementById('choice_ordering_form');
    addRow(form, table)
}
