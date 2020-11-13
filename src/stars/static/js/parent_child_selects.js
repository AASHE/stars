/**
	This tool manages two select inputs that have a parent/child relationship.
	
	When an option from the parent is selected, the child is populated with
	specific options for that parent.
	
	Example HTML:
		
		<select
			data-target='child_select'
			data-target-options='child_options'
			id='parent_select'
		>
			<option value="" selected="selected">-------</option>
			<option value="child_key1">Option 1</option>
			<option value="child_key2">Option 2</option>
		</select>
		<select id='child_select'>
			<option value='' selected='selected'>-------</option>
		</select>
		
	Example Javascript:
		
		child_options = {
			parent_option_key1: [
				['Child Option a1', 'option_a1_value'],
				['Child Option a2', 'option_a2_value']
			],
		
			parent_option_key2: [
				['Child Option b1', 'option_b1_value'],
				['Child Option b2', 'option_b2_value']
			],
		}
		
	Initialize the <select>:
	
		<script type='text/javascript'>
			$('#parent_select').parentChildSelect();
		</script>
		
	Required Parameters:
	
		data-target:
			the id of the child <select>
			
		data-target-options:
			the list of <options> for each child (see "Example Javascript" above)
			
	Possible Improvements:
		
		Auto initialize all any select with the "parent_child_select" class
**/

/**
 * This is the plugin for the parent <select> it will populate the child
 * on change
 */
!function ($) {
	
	$.fn.parentChildSelect = function(){
		
		// Bind the onchange event to the selection populate method
		this.bind('change.parentChildSelect', function(){
			
			var $this = $(this);
			
			// Get the values for data-target and data-target-options
			var $target_select = $("#" + $this.data('target'));
			var $target_choices_list = window[$this.data('targetOptions')];
				
			// Remove all options from the child
			$target_select.empty()
			
			// Repopulate the child
			if ($this.val() != "") {
				$target_select.append($("<option></option>").attr("value", '').text('------'));
				$.each($target_choices_list[$this.val()], function(key, value) {
					$target_select.append($("<option></option>")
					.attr("value", value).text(key));
				});	
			}
		});
	};
	
}(window.jQuery);