#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from Automata.NFA2DFA import *
from django.shortcuts import render_to_response
#test样例，json格式
FA = {
        'type':'NFA',
        #'input':[
        #    0,
        #    1,
        #],
        'state':{
            'A':{
                'name':'A',
                'is_start':True,
                'is_final':False,
                'transition':{
                    '0':['B'],
                    '1':['F'],
                }
            },
            'B':{
                'name':'B',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['G'],
                    '1':['C'],
                }
            },
            'C':{
                'name':'C',
                'is_start':False,
                'is_final':True,
                'transition':{
                    '0':['A'],
                    '1':['C'],
                }
            },
            'D':{
                'name':'D',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['C'],
                    '1':['G'],
                }
            },
            'E':{
                'name':'E',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['H'],
                    '1':['F'],
                }
            },
            'F':{
                'name':'F',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['C'],
                    '1':['G'],
                }
            },
            'G':{
                'name':'G',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['G'],
                    '1':['E'],
                }
            },
            'H':{
                'name':'H',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['G'],
                    '1':['C'],
                }
            },
        },
        'input':['0','1'],
        'start':'A',
        'final':['C'],
    }
DFA = {
        'type':'NFA',
        'state':{
            'q0':{
                'name':'q0',
                'is_start':True,
                'is_final':False,
                'transition':{
                    u'ε':['q0','q1'],
                    '+':['q1'],
                }
            },
             'q1':{
                'name':'q1',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '.':['q2'],
                    '0':['q1','q4'],
                    '1':['q1','q4'],
                }
            },
             'q2':{
                'name':'q2',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['q3'],
                    '1':['q3'],
                }
            },
             'q3':{
                'name':'q3',
                'is_start':False,
                'is_final':False,
                'transition':{
                    u'ε':['q5'],
                    '0':['q3'],
                    '1':['q3'],
                }
            },
             'q4':{
                'name':'q4',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '.':['q3'],
                }
            },
             'q5':{
                'name':'q5',
                'is_start':False,
                'is_final':True,
                'transition':{
                }
            },
        },
        'input':['0','1','.','+',u'ε'],
        'start':'q0',
        'final':['q5'],
    }




#NFA转DFA函数
def judgeFA(request):
    global FA
    #从前端得到FA和judgeString的值
    #FA = simplejson.loads(request.raw_post_data)
    #judgeString = simplejson.loads(request.raw_post_data)

    judgeString = '01111001011101' #待判断的语句
    #judgeString = '01' #待判断的语句
    #index = 0        #当前执行到的语句位置

    #如果是空语句
    if judgeString == '':
        return HttpResponse(FA['state'][FA['start']] in FA['final'])
    return HttpResponse(per_judgeFA(FA,FA['start'],judgeString,index))


#递归每一步的判断
def per_judgeFA(FA,now_state,judgeString,index):
    #输入串完毕
    if index == len(judgeString):
        if FA['state'][now_state]['is_final'] == True:
            return True
        #else:
        #    return False

    ifBelong = False

    #ε转移
    now_transition = FA['state'][now_state]['transition']
    if u'ε' in now_transition:
        for state in now_transition[u'ε']:
            if state != now_state and per_judgeFA(FA,state,judgeString,index):
                return True

    if index == len(judgeString):
        return False
    str = judgeString[index]
    #转移
    if str in now_transition:
        for state in now_transition[str]:
            if per_judgeFA(FA,state,judgeString,index+1):
                return True

    return False
