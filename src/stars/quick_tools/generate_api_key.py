from tastypie.models import ApiKey
from django.contrib.auth.models import User

user_email = raw_input('User Email: ')

try:
    user = User.objects.get(email=user_email)
except:
    print "User Not Found"

if user:
    try:
        api_key = ApiKey.objects.get(user=user)
        print "API key exists: %s" % api_key

    except ApiKey.DoesNotExist:
        api_key = ApiKey.objects.create(user=user)
        print "Created API key: %s" % api_key
