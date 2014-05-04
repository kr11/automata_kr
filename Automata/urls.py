from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf.urls.defaults import *
from Automata.NFA2DFA import *
from Automata.miniDFA import *
from Automata.judgeFA import *
from Automata.judgePDA import *
from Automata.judgeTuring import *
from Automata.CFG2PDA import *
from Automata.PDA2CFG import *
from Automata.convertNP_LP import *
from Automata.RE2DFA import *
from Automata.judgeRE import *
from Automata.DFA2RE_route import *
from Automata.DFA2RE_state import *
#admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'Automata.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    ('^NFA2DFA/$', NFA2DFA),
    ('^judgeFA/$', judgeFA),
    ('^miniDFA/$', miniFDA),
    ('^judgeDFA/$', judgePDA),
    ('^judgeTuring/$', judgeTuring),
    ('^CFG2PDA/$', CFG2PDA),
    ('^PDA2CFG/$', PDA2CFG),
    ('^LP2NP/$', fore_LP2NP),
    ('^NP2LP/$', fore_NP2LP),
    ('^RE2DFA/$', fore_RE2DFA),
    ('^judgeRE/$', judgeRE),
    ('^DFA2RE_route/$',fore_DFA2RE_route),
    ('^DFA2RE_state/$',fore_DFA2RE_state),
    (r'^$',fore_DFA2RE_route),
    #(r'^$',fore_LP2NP),
    #url(r'^admin/', include(admin.site.urls)),
)


