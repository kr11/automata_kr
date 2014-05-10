
#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from Automata.judgeCFG import *
from Automata.PDA2CFG import *
from django.shortcuts import render_to_response
#test样例，json格式

PDA = {
        'type':'PDA',
        'receive':'final',
         'input':['0','1',u'ε'],
         'stack_input':['0','1','Z0'],
        'start_state':'q0',
        'start_stack':'Z0',
        'stack':['Z0'],
        'final':['q2'],
        'state':{
            'q0':{
                'name':'q0',
                'is_start':True,
                'is_final':False,
                'transition':{
                    #上层的ε，0，1为输入符号input
                    #下一层Z0，1，0为输入栈符号
                    u'ε':{

                        'Z0':[['q1',['Z0']],],
                        '0':[['q1',['0']],],
                        '1':[['q1',['1']],],
                    },
                    '0':{
                        #状态q0输入符号ε，栈顶为Z0，则
                        #1. 转到q1，栈顶换成：【0，Z0，……】
                        #2.……
                        'Z0':[['q0',['0','Z0']],],
                        '0':[['q0',['0','0']],],
                        '1':[['q0',['0','1']],],
                    },
                     '1':{
                        'Z0':[['q0',['1','Z0']],],
                        '0':[['q0',['1','0']],],
                        '1':[['q0',['1','1']],],
                    },
                }
            },
            'q1':{
                'name':'q1',
                'is_start':False,
                'is_final':False,
                'transition':{
                    u'ε':{
                        'Z0':[['q2',['Z0']],],
                    },
                    '0':{
                        '0':[['q1',[u'ε']],],
                    },
                     '1':{
                        '1':[['q1',[u'ε']],],
                    },
                }
            },
            'q2':{
                'name':'q2',
                'is_start':False,
                'is_final':True,
                'transition':{
                }
            },
        },
    }
rDA = {
        'type':'PDA',
        'receive':'empty',
         'input':['0','1',u'ε'],
         'stack_input':['0','1','Z0'],
        'start_state':'q0',
        'start_stack':'Z0',
        'stack':['Z0'],
        'final':[],
        'state':{
            'q0':{
                'name':'q0',
                'is_start':True,
                'is_final':False,
                'transition':{
                    #上层的ε，0，1为输入符号input
                    #下一层Z0，1，0为输入栈符号
                    u'ε':{

                        'Z0':[['q1',['Z0']],],
                        '0':[['q1',['0']],],
                        '1':[['q1',['1']],],
                    },
                    '0':{
                        #状态q0输入符号ε，栈顶为Z0，则
                        #1. 转到q1，栈顶换成：【0，Z0，……】
                        #2.……
                        'Z0':[['q0',['0','Z0']],],
                        '0':[['q0',['0','0']],],
                        '1':[['q0',['0','1']],],
                    },
                     '1':{
                        'Z0':[['q0',['1','Z0']],],
                        '0':[['q0',['1','0']],],
                        '1':[['q0',['1','1']],],
                    },
                }
            },
            'q1':{
                'name':'q1',
                'is_start':False,
                'is_final':False,
                'transition':{
                    u'ε':{
                        'Z0':[['q1',[u'ε']],],
                    },
                    '0':{
                        '0':[['q1',[u'ε']],],
                    },
                     '1':{
                        '1':[['q1',[u'ε']],],
                    },
                }
            },

        },
    }
ADA = {
        'type':'PDA',
        'receive':'empty',
        'input':['i','e'],
        'stack_input':['Z'],
        'start_state':'q',
        'start_stack':'Z',
        'stack':['Z'],
        'final':[],
        'state':{
            'q':{
                'name':'q',
                'is_start':True,
                'is_final':False,
                'transition':{
                    'i':{
                        'Z':[['q',['Z','Z']],],
                    },
                     'e':{
                        'Z':[['q',[u'ε']],],
                    },
                }
            },
        },
    }
#NFA转DFA函数
def fore_judgePDA(request):
    global PDA
    #从前端得到FA和judgeString的值
    #PDA = simplejson.loads(request.raw_post_data)
    #judgeString = simplejson.loads(request.raw_post_data)
    judgeString = '010110011010' #待判断的语句
    #judgeString = '0101111010' #待判断的语句
    CFG = PDA2CFG(PDA)
    return HttpResponse(CYKAlgorithm(CFG,judgeString))

