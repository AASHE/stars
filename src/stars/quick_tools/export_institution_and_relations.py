import sys
from itertools import chain

from django.core import serializers
from django.contrib.admin.utils import NestedObjects

from stars.apps.institutions.models import Institution


if len(sys.argv) != 2:
    print("ERROR: No Institution pk specified.")
    print("USAGE: manage.py restore_institution <institution-pk>")
    sys.exit(1)
else:
    pk = sys.argv[1]

collector = NestedObjects(using="stars-backup")

collector.collect(
    [Institution.objects.using("stars-backup").get(pk=pk)])

objects = list(chain.from_iterable(collector.data.values()))

with open("institution_" + str(pk) + ".json", "w") as f:
    f.write(serializers.serialize("json", objects))
