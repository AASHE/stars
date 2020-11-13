import csv, sys

#get_choices_default()

def export_to_file(model, filepath, media_prefix=None):
    """
        Exports all values for a model to a CSV file
        The media_prefix should be in the form http://domain/.
        If used it will be prepended to file and image fields
    """
    
    writer = csv.writer(open(filepath, 'w'))
    # Write headers to CSV file
    headers = []
    # Get all the basic field names
    for field in model._meta.fields:
        headers.append(field.name)
        
    # Get all the ManyToManyField objects
    for m in model._meta.many_to_many:
        # List all the choices in the header
        for r in m.get_choices_default():
            headers.append(r[1])
    writer.writerow(headers)
    
    # Write data to CSV file
    for obj in model.objects.order_by("id"):
        row = []
        for field in model._meta.fields:
            if field.__class__.__name__ == "CharField" or field.__class__.__name__ == "TextField":
                data = getattr(obj, field.name)
                try:
                    row.append(getattr(obj, field.name).encode('utf8'))
                except:
                    print >> sys.stderr, getattr(obj, field.name)
            elif (field.__class__.__name__ == "FileField" or field.__class__.__name__ == "ImageField") and media_prefix:
                row.append("%s%s" % (media_prefix.encode('utf8'), getattr(obj, field.name).__str__().encode('utf8')))
            else:
                row.append(getattr(obj, field.name))
                
        # Add a Boolean to any selected ManyToManyField columns
        for m in model._meta.many_to_many: # for every many-to-many relationship
            
            # get the list of selected m2ms
            selected = []
            m2m = getattr(obj, m.name)
            for s in m2m.all():
                selected.append(s.id)
                
            # go through each option and add True or False to the row
            for o in m.get_choices_default():
                row.append(o[0] in selected)
            
        writer.writerow(row)
