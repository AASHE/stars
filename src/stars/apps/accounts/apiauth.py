import tastypie.authentication
import tastypie.http


# The plan is to combine api-key with username/password authentication.
# That's not working now, so until it is, we're just using api-key auth:

AasheApiAuthentication = tastypie.authentication.ApiKeyAuthentication

# class AasheApiAuthentication(tastypie.authentication.Authentication):

#     def __init__(self):
#         super(AasheApiAuthentication, self).__init__()
#         self.basic_auth = tastypie.authentication.BasicAuthentication()
#         self.api_key_auth = tastypie.authentication.ApiKeyAuthentication()

#     def is_authenticated(self, request, **kwargs):
#         basic_response = self.basic_auth.is_authenticated(request, **kwargs)
#         if isinstance(basic_response, tastypie.http.HttpUnauthorized):
#             return basic_response
#         elif basic_response:
#             api_key_response = self.api_key_auth.is_authenticated(
#                 request, **kwargs)
#             if isinstance(api_key_response, tastypie.http.HttpUnauthorized):
#                 return api_key_response
#             else:
#                 return api_key_response

#     # Optional but recommended
#     def get_identifier(self, request):
#         return self.api_key_auth.get_identifier(request)


# class ApiAuthorization(Authorization):

#     def is_authorized(self, request, object=None):
#         if request.user.date_joined.year == 2010:
#             return True
#         else:
#             return False

#     # Optional but useful for advanced limiting, such as per user.
#     def apply_limits(self, request, object_list):
#         if request and hasattr(request, 'user'):
#             return object_list.filter(author__username=request.user.username)

#         return object_list.none()
