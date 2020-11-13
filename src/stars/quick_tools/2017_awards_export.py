import datetime

from hub.apps.content.types.publications import Publication


just_these_names = ["Journal Article",
                    "Graduate Student Research",
                    "Undergraduate Student Research"]

JUST_THESE_TYPES = []

for publication_material_type in PublicationMaterialType.objects.all():
    if publication_material_type.name in just_these_names:
        JUST_THESE_TYPES.append(publication_material_type)

for publication in Publication.objects.filter(
        date_submitted__gte=datetime.date(2017, 5, 12)).filter(
            date_submitted__lte=datetime.date(2017, 5, 22)):

    if publication.material_type in JUST_THESE_TYPES:

        import ipdb; ipdb.set_trace()
