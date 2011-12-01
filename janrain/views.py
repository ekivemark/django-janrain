from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib import auth
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext
from django.template.defaultfilters import slugify
from rbutton.apps.accounts.models import *
from rbutton.apps.accounts.forms import *

import urllib, urllib2, json

@csrf_exempt
def login(request):
    try:
        token = request.POST['token']
    except KeyError:
        # TODO: set ERROR to something
        return HttpResponseRedirect('/')

    api_params = {
        'token': token,
        'apiKey': settings.JANRAIN_RPX_API_KEY,
        'format': 'json',
    }

    janrain_response = urllib2.urlopen(
            "https://rpxnow.com/api/v2/auth_info",
            urllib.urlencode(api_params))
    resp_json = janrain_response.read()
    auth_info = json.loads(resp_json)

    u = None
    if auth_info['stat'] == 'ok':
        profile = auth_info['profile']
        u = auth.authenticate(profile=profile)
        slugged_u = slugify(u)
        print u
        print slugged_u
        print profile
        print "----Auth_info"
        print auth_info
        print "----End Auth_Info"
        print "---Set UserID"
        if settings.USERID_PRIORITY == 'email':
            try:
                if not profile['email'] is None:
                    print "email:"
                    print profile['email']
                    sel = 'email'
                    # u = profile['email']
            except KeyError:
                print "no email - set to preferredUsername"
                print "preferredUsername(alt):"
                print profile['preferredUsername']
                sel = 'preferredUsername'
                # u = profile['preferredUsername']

        if settings.USERID_PRIORITY == 'preferredUsername':
            print "preferrredUsername:"
            print profile['preferredUsername']
            sel = 'preferredUsername'
            # u = profile['preferredUsername']
        elif settings.USERID_PRIORITY =='UID':
            #default to UID
            print "using UID:"
            print u
            sel = "UID"
        print "--- assignment result"
        print u
        print sel
        print profile['identifier']
        print profile['providerName']
        # print profile['email']
    if u is not None:
        request.user = u
#        request.user = slugged_u
        print request.user
        auth.login(request, u)
#        auth.login(request, slugged_u)

        print "we got through auth.login"
        # up = get_object_or_404(UserProfile, user=request.user)
        # print "did we crash on get UserProfile?"
        # We are crashing on the get UserProfile
        try:
           up_worked = UserProfile.objects.get(user=request.user)
           # check for a UserProfile  - set Create to False if one exists
           print "update"
           create=False
        except UserProfile.DoesNotExist:
           create=True

        if create == True:
            print "create was true - do get or create "
            print "get user"
            user_id = User.objects.get(username=request.user).id
            print user_id
            print "get user.profile"

            up=UserProfile.objects.get_or_create(user=request.user)
            up_worked = UserProfile.objects.get(user=request.user)
            # add an immediate save to see if I can fix display field
            print up
            print up_worked
            print up_worked.display
           
        # print "get down"
        # down = up.get_field(user=request.user).display
        # print down

# Now, in views.py, to access a user's profile, you only need two lines:
# user = User.objects.get(pk = user_id)
# user.userprofile = get_or_create_profile(user)
#
# And, say if you wanted to change a value:
# user.userprofile.security_level = '1'
# user.userprofile.save()



        # print "up display"
        if up_worked.display == 'new_user':
            print "up.display is new_user"
            if sel == 'preferredUsername':
                up_worked.display = profile['preferredUsername']
            elif sel == 'email':
              up_worked.display = profile['email']
            elif sel== 'UID':
                print "assigning display"
                print profile['preferredUsername']
                up_worked.display = profile['preferredUsername']

        up_worked.socialsite = profile['providerName']
        up_worked.socialprofile = profile['identifier']
        if profile['providerName']=='Twitter':
            up_worked.twitter = profile['preferredUsername']
        up_worked.status = 'approved'
        up_worked.save()
        
    try:
        return HttpResponseRedirect(request.GET['redirect_to'])
    except KeyError:
        return HttpResponseRedirect('/')

def logout(request):
    auth.logout(request)
    try:
        return HttpResponseRedirect(request.GET['redirect_to'])
    except KeyError:
        return HttpResponseRedirect('/')

def loginpage(request):
    context = {'next':request.GET['next']}
    return render_to_response(
        'janrain/loginpage.html',
        context,
        context_instance=RequestContext(request)
    )
    
