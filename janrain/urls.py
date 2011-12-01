from django.conf.urls.defaults import *

urlpatterns = patterns('rbutton.apps.janrain.views',
    (r'^login/$', 'login'),
    (r'^logout/$', 'logout'),
    (r'^loginpage/$', 'loginpage'),
)
