from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.defaults import *
from Automata.NFA2DFA import *
from Automata.miniDFA import *
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Automata.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    ('^NFA2DFA/$', NFA2DFA),
    ('^miniDFA/$', miniFDA),
    (r'^$',miniFDA),
    #url(r'^admin/', include(admin.site.urls)),
)


