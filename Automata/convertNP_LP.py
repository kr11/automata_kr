#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
#from Automata.NFA2DFA import *
from django.shortcuts import render_to_response
import copy
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
        'pre_state':{},
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
    'pre_state':{},
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
    if LP_PDA['state'] == {}:
        parse_2_state(LP_PDA)
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
    connnect_2_pre_state(LP_PDA)
    return  LP_PDA


#NP（空栈）转 LP(终态)
def NP2LP(NP_PDA):
    if NP_PDA['receive'] != 'empty':
        return 0
    #添加新的栈底元素
    if NP_PDA['state'] == {}:
        parse_2_state(NP_PDA)
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
    connnect_2_pre_state(NP_PDA)
    return  NP_PDA

#将拆开的state连接成pre_state
def connnect_2_pre_state(PDA):
    PDA['pre_state'] = copy.deepcopy(PDA['state'])
    for m_state in PDA['state']:
        for m_input in PDA['state'][m_state]['transition']:
            temp_trans = PDA['state'][m_state]['transition']
            PDA['pre_state'][m_state]['transition'][m_input] = {}
            #扫描，添加
            for stack_top in temp_trans[m_input]:
                for tran_list in temp_trans[m_input][stack_top]:
                    to_state = tran_list[0]
                    tran_str = stack_top + '/' +  ''.join(tran_list[1])
                    if to_state not in PDA['pre_state'][m_state]['transition'][m_input]:
                        PDA['pre_state'][m_state]['transition'][m_input][to_state] = []
                    PDA['pre_state'][m_state]['transition'][m_input][to_state].append(tran_str)
    return PDA

#将连在一起的pre_state拆分成state
def parse_2_state(PDA):
    PDA['state'] = copy.deepcopy(PDA['pre_state'])
    for m_state in PDA['pre_state']:
        for m_input in PDA['pre_state'][m_state]['transition']:
            temp_trans = PDA['pre_state'][m_state]['transition']
            PDA['state'][m_state]['transition'][m_input] = {}
            #扫描，添加
            for to_state in temp_trans[m_input]:
                for tran_str in temp_trans[m_input][to_state]:
                    stack_top,fin_trans = per_parse_sta(to_state,tran_str,PDA['stack_input'])
                    if stack_top == '' and fin_trans == []:
                        return []
                    if stack_top not in PDA['state'][m_state]['transition'][m_input]:
                        PDA['state'][m_state]['transition'][m_input][stack_top] = []
                    PDA['state'][m_state]['transition'][m_input][stack_top].append(fin_trans)
    return PDA

def per_parse_sta(to_state,tran_str,stack_input):
    result = []
    tran_str = tran_str.split('/')
    if len(tran_str) != 2 or tran_str[0] not in stack_input:
        return '',[]
    stack_top = tran_str[0]
    #当前扫描位置
    index = 0
    while(index < len(tran_str[1])):
        #ε转移情况
        if tran_str[1][index] == u'ε':
            if tran_str[1] == u'ε':
                return stack_top,[to_state,[u'ε']]
            else:
                index += 1
                continue
        iffound = False
        for i in range(index+1,len(tran_str[1])+1):
            temp = tran_str[1][index:(len(tran_str[1])+index+1-i)]
            if temp in stack_input:
                index = len(tran_str[1])+index-i+1
                result.append(temp)
                iffound = True
                break
        if iffound == False:
            return '',[]
    return stack_top,[to_state,result]



#将拆开的final_Production连接成pre_Production
def connnect_preP(CFG):
    temp_prduct = copy.deepcopy(CFG['pre_Production'])
    for fore in temp_prduct:
        if fore not in CFG['final_Production']:
            CFG['pre_Production'].pop(fore)
    for fore in CFG['final_Production']:
        #CFG['pre_Production'][fore] = ''
        temp = []
        for trans in CFG['final_Production'][fore]:
            temp.append(''.join(trans))
        CFG['pre_Production'][fore] = '|'.join(temp)
            #CFG['pre_Production'][fore] += ''.join(trans)
    return CFG

#将连在一起的pre_Production拆分成final_Production
def parse_finalP(CFG):
    temp_prduct = copy.deepcopy(CFG['final_Production'])
    for fore in temp_prduct:
        if fore not in CFG['pre_Production']:
            CFG['final_Production'].pop(fore)
    for fore in CFG['pre_Production']:
        product = CFG['pre_Production'][fore].split('|')
        index = 0
        CFG['final_Production'][fore] = []
        for per_pro in product:
            if per_pro == u'ε':
                CFG['final_Production'][fore].append([u'ε'])
                continue
            #将每个连起来的串分割成有终结符或变元组成的数组
            temp = parsePro(per_pro,CFG['Variable'],CFG['Terminal'])
            if temp == []:
                return [] #[]说明出错，返回
            else:
                CFG['final_Production'][fore].append(temp)
    return CFG

def parsePro(per_pro,Var,Ter):
    list = []
    #当前扫描位置
    index = 0
    #终结符
    while(index < len(per_pro)):
        iffound = False
        for i in range(index+1,len(per_pro)+1):
            temp = per_pro[index:(len(per_pro)+index+1-i)]
            if temp in Var or temp in Ter:
                index = len(per_pro)+index-i+1
                list.append(temp)
                iffound = True
                break
        if iffound == False:
            return []
    return list

