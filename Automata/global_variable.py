#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
#from Automata.NFA2DFA import *
from django.shortcuts import render_to_response

preDFA = {}
NFA = {}