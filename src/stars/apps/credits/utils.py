from functools32 import lru_cache


@lru_cache()
def get_mappings():
    """
    Return a list of var names for mapping ints to variable names

    List has 6 * 26 elements.  If you need more variable names than
    that, this function is insufficient.
    """

    var_names = []
    for i in range(0, 26):
        var_names.append(chr(i+65))

    for i in range(0, 5):
        for j in range(0, 26):
            var_names.append("%s%s" % (chr(i+65), chr(j+65)))

    return var_names


@lru_cache()
def int_to_var(num):
    """
    converts a number to a unique variable name
    """
    mappings = get_mappings()

    return mappings[num]


@lru_cache()
def var_to_int(var):
    """
    converts a variable name to a unique number
    """

    mappings = get_mappings()
    return mappings.index(var)


def get_next_variable_name(variable_list):
    """
    Takes a list of variable names and returns a new unique one.

    Variables are structured as so:
    A > B > B > ... > Z > AA > AB > ... > AZ > BA > BB > BC
    """

    v = 'A'
    if not variable_list:
        return v

    # convert all vars in list to numeric form
    num_list = []
    for v in variable_list:
        num_list.append(var_to_int(v))

    # get the highest number in the list and add one
    num_list.sort()
    next_num = num_list[-1] + 1

    # convert to variable name
    return int_to_var(next_num)


def get_array_for_tabular_fields(df):
    """
        Takes a DocumentationField of the tabular variety
        and returns an array with all the headers and
        sub-documentation_fields

        [[None, ColHeader, ...,],
         [Row Header, DF, ...,],
         ...,
         ]
    """
    from models import DocumentationField

    table = []

    # add the top row
    row = [None]
    for h in df.tabular_fields['colHeadings']:
        row.append(h)
    table.append(row)

    # add the left columns
    for h in df.tabular_fields['rowHeadings']:
        table.append([h])

    # now fill in the fields
    c = 1
    tabular_fields = df.tabular_fields['fields']

    for col in tabular_fields:
        for cell in col:
            if cell:
                df = DocumentationField.objects.get(pk=int(cell))
            else:
                df = ''
            table[c].append(df)
        c += 1

    return table
