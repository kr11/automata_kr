#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from Automata.PDA2CFG import *
from Automata.convertNP_LP import *
from django.shortcuts import render_to_response
import copy
#test样例，json格式

PDA = {
        'type':'PDA',
        'receive':'empty',
         'input':[],
         'stack_input':[],
        'start_state':'q0',
        'start_stack':'S',
        'stack':['S'],
        'final':['q0'],
        'pre_state':{},
        'state':{
            'q0':{
                'name':'q0',
                'is_start':True,
                'is_final':False,
                'transition':{
                }
            },
        }
    }
#上下无关文法
CFG = {
        'type':'CFG',
        'Variable':['I','E'],
        'Terminal':['a','b','0','1','(',')','+','*'],
        'Start':'E',
        'pre_Production':{
            'I':'a|b|Ia|Ib|I0|I1',
            'E':'I|E*E|E+E|(E)',
        },
        'final_Production':{
            #'S':[['i','S','S'],['e']],
        }
    }
def fore_CFG2PDA(request):
    global CFG
    #CFG = simplejson.loads(request.raw_post_data)
    PDA = CFG2PDA(CFG)
    json=simplejson.dumps(PDA)
    return HttpResponse(json)


#NFA转DFA函数
def CFG2PDA(CFG):
    #从前端得到FA和judgeString的值
    CFG = parse_finalP(CFG)
    if CFG == []:
        return []
    #初始化PDA
    PDA = {
            'type':'PDA',
            'receive':'empty',
             'input':[],
             'stack_input':[],
            'start_state':'q0',
            'start_stack':'S',
            'stack':['S'],
            'final':['q0'],
            'pre_state':{},
            'state':{
                'q0':{
                    'name':'q0',
                    'is_start':True,
                    'is_final':False,
                    'transition':{
                    }
                },
            }
        }
    PDA['input'] = copy.deepcopy(CFG['Terminal'])
    PDA['stack_input'] = list(set(CFG['Terminal'])|set(CFG['Variable']))
    PDA['start_stack'] = CFG['Start']
    PDA['stack'] = [CFG['Start']]

    #定义转移函数
    #变元
    PDA['state']['q0']['transition'][u'ε'] = {}
    for A in CFG['Variable']:
        PDA['state']['q0']['transition'][u'ε'][A] = []
        for prc in CFG['final_Production'][A]:
            PDA['state']['q0']['transition'][u'ε'][A].append(['q0',prc])
    #终结符
    for ter in CFG['Terminal']:
        PDA['state']['q0']['transition'][ter] = {}
        PDA['state']['q0']['transition'][ter][ter] = [['q0',[u'ε']]]
    PDA = connnect_2_pre_state(PDA)
    return PDA




