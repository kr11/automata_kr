#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson

from Automata.RE2DFA import *
from Automata.judgeFA import *




#NFA转DFA函数
def judgeRE(request):
    REstring = '' #正则表达式
    judgeString = '01111001011101' #待判断的语句
    #从前端得到REString和judgeString的值
    #REstring = simplejson.loads(request.raw_post_data)
    #judgeString = simplejson.loads(request.raw_post_data)

    #转化为自动机
    DFA = RE2DFA(REstring)
    #如果是空语句
    if judgeString == '':
        return HttpResponse(DFA['state'][DFA['start']] in DFA['final'])
    return HttpResponse(per_judgeFA(DFA,DFA['start'],judgeString,0))


