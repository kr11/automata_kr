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

                        'Z0':[['q1',['0','Z0']],],
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


#NFA转DFA函数
def judgePDA(request):
    global PDA
    #从前端得到FA和judgeString的值
    #FA = simplejson.loads(request.raw_post_data)
    #judgeString = simplejson.loads(request.raw_post_data)

    judgeString = '01111001011101' #待判断的语句
    #judgeString = '' #待判断的语句
    index = 0        #当前执行到的语句位置

    #如果是空语句
    if judgeString == '':
        return HttpResponse(PDA['state'][PDA['start_state']]['is_final'])
    #return HttpResponse(False)
    return HttpResponse(per_judgePDA(PDA,PDA['start_state'],judgeString,index))


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
                    PDA['stack'].pop()
                    state[1].reverse()
                    PDA['stack'] += state[1]
                    state[1].reverse()
                    return per_judgePDA(PDA,state[0],judgeString,index)

    if index == len(judgeString):
        return False
    str = judgeString[index]
    #转移
    if str in now_transition:
        if stack_top in now_transition[u'ε']:
            for state in now_transition[u'ε'][stack_top]:
                if (state[0] != now_state or state[1] != [stack_top]):
                    PDA['stack'].pop()
                    state[1].reverse()
                    PDA['stack'] += state[1]
                    state[1].reverse()
                    return per_judgePDA(PDA,state[0],judgeString,index)


    return False
