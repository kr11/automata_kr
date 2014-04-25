#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from Automata.NFA2DFA import *
from django.shortcuts import render_to_response
#test样例，json格式

Turing = {
        'type':'Turing',
        'input':['0','1'],
        'tape_input':['0','1','X','Y','B'],
        'space':'B',
        'start_state':'q0',
        'final':['q4'],
        #left和right是带头左边和右边的半无限长带（两个栈），栈顶为带头的左右
        'left_tape':[],
        'right_tape':[],
        'state':{
            'q0':{
                'name':'q0',
                'is_start':True,
                'is_final':False,
                'transition':{
                    '0':['q1','X','R'],
                    'Y':['q3','Y','R'],
                }
            },
            'q1':{
                'name':'q1',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['q1','0','R'],
                    '1':['q2','Y','L'],
                    'Y':['q1','Y','R'],
                }
            },
            'q2':{
                'name':'q2',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['q2','0','L'],
                    'X':['q0','X','R'],
                    'Y':['q2','Y','L'],
                }
            },
            'q3':{
                'name':'q3',
                'is_start':False,
                'is_final':False,
                'transition':{
                    'Y':['q3','Y','R'],
                    'B':['q4','B','R'],
                }
            },
            'q4':{
                'name':'q4',
                'is_start':False,
                'is_final':True,
                'transition':{
                }
            },
        },
    }

#NFA转DFA函数
def judgeTuring(request):
    global Turing
    #从前端得到FA和judgeString的值
    #Turing = simplejson.loads(request.raw_post_data)
    #judgeString = simplejson.loads(request.raw_post_data)

    judgeString = '0000000011111111' #待判断的语句


    #如果是空语句
    if judgeString == '':
        return HttpResponse(Turing['state'][Turing['start_state']]['is_final'])

    #初始化左右tape，最开始所有输入均在带头右侧
    Turing['left_tape'].append(Turing['space'])
    Turing['right_tape'].append(Turing['space'])
    #将input压入右半区
    for i in range(0,len(judgeString)):
        Turing['right_tape'].append(judgeString[-1-i])

    return HttpResponse(per_judgeTuring(Turing,Turing['start_state'],Turing['right_tape'][-1]))


def per_judgeTuring(Turing,now_state,now_tape):
    #now_tape:当前带头所指的位置，也是右半区的第一个元素
    #到达终态
    if Turing['state'][now_state]['is_final']:
        return True
    #ε转移
    now_transition = []
    if now_state in Turing['state']:
        now_transition = Turing['state'][now_state]['transition']
    else:
        return False
    #转移
    #if str in now_transition:
    if now_tape in now_transition:# and now_transition[now_state] == 1:
        state = now_transition[now_tape]
        #将当前带头元素替换为state[1]
        Turing['right_tape'][-1] = state[1]
        #移动带头元素
        if state[2] == 'L':
            Turing['right_tape'].append(Turing['left_tape'].pop())
        elif state[2] == 'R':
            Turing['left_tape'].append(Turing['right_tape'].pop())
        else:
            return False
        #对空格情况进行修整
        space = Turing['space']
        if Turing['right_tape'] == [] or Turing['right_tape'] == [space,space] or\
                        Turing['right_tape'] == [space,space,space]:
            Turing['right_tape'] = [space]
        if Turing['left_tape'] == [] or Turing['left_tape'] == [space,space] or\
                        Turing['left_tape'] == [space,space,space]:
            Turing['left_tape'] = [space]
        #递归
        return per_judgeTuring(Turing,state[0],Turing['right_tape'][-1])
    return False
