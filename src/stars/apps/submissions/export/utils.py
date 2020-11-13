from django.conf import settings

def getRatingImage(rating):
    # Ex: Stars_Seal_Bronze_RGB_300.png
    return "%s/images/seals/Stars_Seal_%s_RGB_300.png" % (settings.STATIC_ROOT, rating.name)
