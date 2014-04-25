#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from Automata.NFA2DFA import *
from django.shortcuts import render_to_response
#终态结束的PDA
LP_PDA = {
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

NP_PDA = {
    "type":"PDA",
    "receive":"empty",
    "stack_input":["0","1","Z0","X0"],
    "start_state":"P0",
    "input":["0","1",u"ε",'P0','P1'],
    "start_stack":"X0",
    "stack":["X0"],
    "final":[],
    "state":{
        "q1":{
            "name":"q1",
            "is_start":False,
            "is_final":False,
            "transition":{
                "0":{
                    "0":[["q1",[u"ε"]]]
                },
                "1":{
                    "1":[["q1",[u"ε"]]]
                },
                u"ε":{
                    "Z0":[["q2",["Z0"]]]
                }
            },
        },
        "q0":{
            "name":"q0",
            "is_start":False,
            "is_final":False,
            "transition":{
                "0":{
                    "0":[["q0",["0","0"]]],
                    "1":[["q0",["0","1"]]],
                    "Z0":[["q0",["0","Z0"]]]
                },
                "1":{
                    "0":[["q0",["1","0"]]],
                    "1":[["q0",["1","1"]]],
                    "Z0":[["q0",["1","Z0"]]]
                },
                u"ε":{
                    "0":[["q1",["0"]]],
                    "1":[["q1",["1"]]],
                    "Z0":[["q1",["Z0"]]]
                }
            },
        },
        "P0":{
            "name":"P0",
            "is_start":True,
            "is_final":False,
            "transition":{
                u"ε":{
                    "X0":[["q0",["Z0","X0"]]]
                }
            },

        },
        "q2":{
            "name":"q2",
            "is_start":False,
            "is_final":True,
            "transition":{
                u"ε":{
                    "0":[["P1",[u"ε"]]],
                    "1":[["P1",[u"ε"]]],
                    "X0":[["P1",[u"ε"]]],
                    "Z0":[["P1",[u"ε"]]]
                }
            },
        },
        "P1":{
            "name":"P1",
            "is_start":False,
            "is_final":True,
            "transition":{
                u"ε":{
                    "0":[["P1",[u"ε"]]],
                    "1":[["P1",[u"ε"]]],
                    "X0":[["P1",[u"ε"]]],
                    "Z0":[["P1",[u"ε"]]]
                }
            },
        }
    },
}
#接受前端的信息，调用
def fore_LP2NP(request):
    #从前端得到FA和judgeString的值
    global LP_PDA
    #LP_PDA = simplejson.loads(request.raw_post_data)
    json=simplejson.dumps(LP2NP(LP_PDA))
    return HttpResponse(json)

#接受前端的信息，调用
def fore_NP2LP(request):
    #从前端得到FA和judgeString的值
    global NP_PDA
    #NP_PDA = simplejson.loads(request.raw_post_data)
    json=simplejson.dumps(NP2LP(NP_PDA))
    return HttpResponse(json)

#LP(终态)转NP（空栈）
def LP2NP(LP_PDA):
    if LP_PDA['receive'] != 'final':
        return 0
    #添加新的栈底元素
    addBottom = 'X'
    #保证未出现过
    temp = 0;
    while 1:
        if (addBottom + str(temp)) not in LP_PDA['stack_input']:
            addBottom = addBottom + str(temp);
            break
        else:
            temp += 1
    #添加新的初始元素
    addStart = 'P'
    #保证未出现过
    temp = 0;
    while 1:
        if (addStart + str(temp)) not in LP_PDA['input']:
            addStart = addStart + str(temp);
            temp += 1
            break
        else:
            temp += 1
    #添加新的最终元素
    addFinal = 'P'
    #保证未出现过
    while 1:
        if (addFinal + str(temp)) not in LP_PDA['input']:
            addFinal = addFinal + str(temp);
            break
        else:
            temp += 1

    #添加p0到q0的转移
    pre_start_stack = LP_PDA['start_stack']
    pre_start_state = LP_PDA['start_state']
    LP_PDA['start_stack'] = addBottom
    LP_PDA['stack_input'].append(addBottom)
    LP_PDA['input'].append(addStart)
    LP_PDA['input'].append(addFinal)
    LP_PDA['stack'] = [addBottom]
    LP_PDA['state'][pre_start_state]['is_start'] = False
    LP_PDA['start_state'] = addStart

    LP_PDA['state'][addStart] = {
                'name':addStart,
                'is_start':True,
                'is_final':False,
                'transition':{
                    u'ε':{
                        addBottom:[[pre_start_state,[pre_start_stack,addBottom]],]
                    },
                }
            }

    #添加终态状态
    LP_PDA['state'][addFinal] = {
                'name':addFinal,
                'is_start':False,
                'is_final':True,
                'transition':{
                    u'ε':{
                    }
                }
            }
    #终态的转移
    for stack in LP_PDA['stack_input']:
        #原来的终态
        for final_state in LP_PDA['final']:
            if u'ε' not in  LP_PDA['state'][final_state]['transition']:
                LP_PDA['state'][final_state]['transition'][u'ε'] = {stack:[[addFinal,[u'ε']],]}
            LP_PDA['state'][final_state]['transition'][u'ε'][stack] = [[addFinal,[u'ε']],]
        #现在的终态（空态）
        LP_PDA['state'][addFinal]['transition'][u'ε'][stack] = [[addFinal,[u'ε']],]

    LP_PDA['final'] = []
    LP_PDA['receive'] = 'empty'

    return  LP_PDA


#NP（空栈）转 LP(终态)
def NP2LP(NP_PDA):
    if NP_PDA['receive'] != 'empty':
        return 0
    #添加新的栈底元素
    addBottom = 'X'
    #保证未出现过
    temp = 0;
    while 1:
        if (addBottom + str(temp)) not in NP_PDA['stack_input']:
            addBottom = addBottom + str(temp);
            break
        else:
            temp += 1
    #添加新的初始元素
    addStart = 'P'
    #保证未出现过
    temp = 0;
    while 1:
        if (addStart + str(temp)) not in NP_PDA['input']:
            addStart = addStart + str(temp);
            temp += 1
            break
        else:
            temp += 1
    #添加新的最终元素
    addFinal = 'P'
    #保证未出现过
    while 1:
        if (addFinal + str(temp)) not in NP_PDA['input']:
            addFinal = addFinal + str(temp);
            break
        else:
            temp += 1

    #添加p0到q0的转移
    pre_start_stack = NP_PDA['start_stack']
    pre_start_state = NP_PDA['start_state']
    NP_PDA['start_stack'] = addBottom
    NP_PDA['stack_input'].append(addBottom)
    NP_PDA['input'].append(addStart)
    NP_PDA['input'].append(addFinal)
    NP_PDA['stack'] = [addBottom]
    NP_PDA['state'][pre_start_state]['is_start'] = False
    NP_PDA['start_state'] = addStart

    NP_PDA['state'][addStart] = {
                'name':addStart,
                'is_start':True,
                'is_final':False,
                'transition':{
                    u'ε':{
                        addBottom:[[pre_start_state,[pre_start_stack,addBottom]],]
                    },
                }
            }

    #终态的转移
    for final_state in NP_PDA['state']:
        if final_state != addStart:
            if u'ε' not in  NP_PDA['state'][final_state]['transition']:
                NP_PDA['state'][final_state]['transition'][u'ε'] = {}
            NP_PDA['state'][final_state]['transition'][u'ε'][addBottom] = [[addFinal,[u'ε']],]

    NP_PDA['final'] = [addFinal]
    NP_PDA['receive'] = 'final'

    #添加终态状态
    NP_PDA['state'][addFinal] = {
                'name':addFinal,
                'is_start':False,
                'is_final':True,
                'transition':{
                }
            }

    return  NP_PDA

