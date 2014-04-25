#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from Automata.NFA2DFA import *
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
#上下无关文法
CFG = {
        'type':'CFG',
        'Variable':['S'],
        'Terminal':['i','e'],
        'Start':'S',
        'pre_Production':{
            'S':'iSS|e'
        },
        'final_Production':{
            'S':[['i','S','S'],['e']],
        }
    }
#将拆开的final_Production连接成pre_Production
def connnect_preP():
    return 0

#将连在一起的pre_Production拆分成final_Production
def parse_finalP():
    return 0


#初始化add_new_state，将所有[qXp]编号，放入
def number_addNewState():
    num = 0
    for i in DFA['stack_input']:
        for s in DFA['state']:
            for r in DFA['state']:
                add_new_state[i+s+r] = num
                num += 1
    #return 0

add_new_state = {}#已经重命名过的新状态，对应他的新名字
#NFA转DFA函数
def PDA2CFG(request):
    global PDA
    #从前端得到FA和judgeString的值
    #PDA = simplejson.loads(request.raw_post_data)

    new_state_count = 0   #下一次添加状态‘Q’+ new_state_count
    #初始化CFG
    CFG = {
        'type':'CFG',
        'Variable':['S'],
        'Terminal':[],
        'Start':'S',
        'pre_Production':{
        },
        'final_Production':{
        }
    }

    #初始化add_new_state，将所有[qXp]编号，放入
    number_addNewState()
    #加入初始状态

    #不断加入所有的转移状态

    json=simplejson.dumps(CFG)
    return HttpResponse(json)


def per_judgePDA(PDA,now_state,judgeString,index):
    #栈空为错
    if PDA['stack'] == []:
        return  False
    #输入串完毕
    if index == len(judgeString):
        if PDA['state'][now_state]['is_final']:
            return True
    #ε转移
    now_transition = PDA['state'][now_state]['transition']
    stack_top = PDA['stack'][-1]
    if u'ε' in now_transition:
        if stack_top in now_transition[u'ε']:
            for state in now_transition[u'ε'][stack_top]:
                if (state[0] != now_state or state[1] != [stack_top]):
                    #替换
                    temp = PDA['stack'].pop()
                    if state[1] != [u'ε']:
                        state[1].reverse()
                        PDA['stack'] += state[1]
                        state[1].reverse()
                    if per_judgePDA(PDA,state[0],judgeString,index):
                        return True
                    #还原
                    if state[1] != [u'ε']:
                        for i in range(0,len(state[1])):
                            PDA['stack'].pop()
                    PDA['stack'] += [temp]
    if index == len(judgeString):
        return False
    str = judgeString[index]
    #转移
    if str in now_transition:
        if stack_top in now_transition[str]:
            for state in now_transition[str][stack_top]:
                if (state[0] != now_state or state[1] != [stack_top]):
                    #替换
                    temp = PDA['stack'].pop()
                    if state[1] != [u'ε']:
                        state[1].reverse()
                        PDA['stack'] += state[1]
                        state[1].reverse()
                    if per_judgePDA(PDA,state[0],judgeString,index+1):
                        return True
                    #还原
                    if state[1] != [u'ε']:
                        for i in range(0,len(state[1])):
                            PDA['stack'].pop()
                    PDA['stack'] += [temp]
    return False
