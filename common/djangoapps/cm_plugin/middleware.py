from django.http import HttpResponse
import json
import time
from django.utils.http import cookie_date
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
import aes
from credentials import cm_credentials
import urllib

# ugly.
# this is the mother of all insecure authentication systems.
# TODO: share secret key between edx and cm and send token values
# with AES encryption.


class ExternalAuthMiddleware(object):

    def auth_user(self, request, email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            user = None
        
        if user is not None and user.is_active:
            try:
                # actual authentication
                user = authenticate(email=email)
                login(request, user)
                request.user = user
            except Exception as e:
                raise # probably memcache is down


    def process_request(self, request):
        # ugly hack 1
        # authenticate user based on email. This will be a non persistent authentication
        # required to bypass djangos @login_required decorator. no session or cookie can
        # be set here.
        
        if request.method == 'GET':
            token = request.GET.get('token', '')
		
            user = None
            
            if not token == '':
                if request.user is not None and request.user.is_authenticated():
                    key = cm_credentials('shared_secret')[0:16]
                    token = aes.decrypt(token, key)
                    if not request.user.email == token:
                        self.auth_user(request, token)
                else:
                    # check validity
                    key = cm_credentials('shared_secret')
                    key = key[0:16]
                    token = aes.decrypt(token, key)
                    self.auth_user(request, token)


    def process_response(self, request, response):
        # ugly hack 2
        # this takes the response from the logged in view, authenticates the user again based on token,
        # adds user session to memcache and sends a cookie back to browser.
        # This makes sure that the entire auth process is successful.

        token = request.GET.get('token', '')
        user = None
        if hasattr(request, 'user'):
            if request.user.is_authenticated():
                return response
            if not token == '':
                try:
                    key = cm_credentials('shared_secret')[0:16]
                    token = aes.decrypt(token, key)
                    user = User.objects.get(email=token)
                except:
                    user = None
                    
            if user is not None and user.is_active:
                try:
                    # We do not log here, because we have a handler registered
                    # to perform logging on successful logins.
                    key = cm_credentials('shared_secret')[0:16]
                    token = aes.decrypt(token, key)
                    user = authenticate(email=token)
                    login(request, user)
                    request.session.set_expiry(604800)
                except Exception as e:
                    raise
                
        max_age = 1209600
        expires_time = time.time() + max_age
        expires = cookie_date(expires_time)

        response.set_cookie(settings.EDXMKTG_COOKIE_NAME,
                            'true', max_age=max_age,
                            expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                            path='/',
                            secure=None,
                            httponly=None)

        return response
