from django.contrib.auth.models import User
from hashlib import sha1
from base64 import b64encode
from django.conf import settings
import re

class JanrainBackend(object):

    def authenticate(self, profile):
        # django.contrib.auth.models.User.username is required and 
        # has a max_length of 30 so to ensure that we don't go over 
        # 30 characters we base64 encode the sha1 of the identifier 
        # returned from janrain 
        hashed_user = b64encode(sha1(profile['identifier']).digest())
        # we need to remove invalid characters from the hash
        hashed_user = self.clean_64(hashed_user)

        try :
            u = User.objects.get(username=hashed_user)
        except User.DoesNotExist:

            fn, ln = self.get_name_from_profile(profile)
            u = User(
                    username=hashed_user,
                    password='',
                    first_name=fn,
                    last_name=ln,
                    email=self.get_email(profile)
                )
            # Set an unusable password to protect unauthorized access.
            u.set_unusable_password()
            u.is_active = True
            u.is_staff = False
            u.is_superuser = False
            u.save()
        return u

    def get_user(self, uid):
        try:
            return User.objects.get(pk=uid)
        except User.DoesNotExist:
            return None

    def get_name_from_profile(self, p):
        nt = p.get('name')
        if type(nt) == dict:
            fname = nt.get('givenName')
            lname = nt.get('familyName')
            if fname and lname:
                return (fname, lname)
        dn = p.get('displayName')
        if len(dn) > 1 and dn.find(' ') != -1:
            (fname, lname) = dn.split(' ', 1)
            return (fname, lname)
        elif dn == None:
            return ('', '')
        else:
            return (dn, '')

    def get_email(self, p):
        return p.get('verifiedEmail') or p.get('email') or ''

    def clean_64(self, string):
        try:
            clean_string = ''

            for character in string:
                
                if re.search(character,settings.CLEAN_USERNAME_CHARS):
                    # if character is a clean character append to new string
                    clean_string = clean_string + character
                else:
                    # replace character with an underscore before appending
                    new_character = '_'
                    clean_string = clean_string + new_character
                    print "changed: "  + character + " to " + new_character

        except:
            return clean_string
        print "clean string:"
        print clean_string
        print "dirty string:"
        print string
        return clean_string

    