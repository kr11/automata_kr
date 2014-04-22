#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from Automata.NFA2DFA import *
from django.shortcuts import render_to_response
#test样例，json格式
pre_DFA = {
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
                    '0':'B',
                    '1':'F',
                }
            },
            'B':{
                'name':'B',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':'G',
                    '1':'C',
                }
            },
            'C':{
                'name':'C',
                'is_start':False,
                'is_final':True,
                'transition':{
                    '0':'A',
                    '1':'C',
                }
            },
            'D':{
                'name':'D',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':'C',
                    '1':'G',
                }
            },
            'E':{
                'name':'E',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':'H',
                    '1':'F',
                }
            },
            'F':{
                'name':'F',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':'C',
                    '1':'G',
                }
            },
            'G':{
                'name':'G',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':'G',
                    '1':'E',
                }
            },
            'H':{
                'name':'H',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':'G',
                    '1':'C',
                }
            },
        },
        'input':['0','1'],
        'start':'A',
        'final':['C'],
    }
miniFDA = {} #待返回的DFA结构体
equal_pair = [] #等价对，填表法专用

#NFA转DFA函数
def miniFDA(request):
    global mini_DFA,pre_DFA,equal_pair,pre_NFA
    #pre_DFA = simplejson.loads(request.raw_post_data)
    #pre_DFA = pre_NFA
    init_miniDFA()
    file_table()
    rebuild_NDA()
    json=simplejson.dumps(mini_DFA)
    return HttpResponse(json)


#初始化
def init_miniDFA():
    global mini_DFA,pre_DFA,equal_pair
    mini_DFA = {
        'type':'DFA',
        'state':{
        },
        'input':[],
        'start':'',
        'final':[],
    }
    #将各状态对存入数组中，规则前小后大
    for state1 in pre_DFA['state']:
        for state2 in pre_DFA['state']:
            if state1 < state2:
                equal_pair.append([state1,state2])
                #print equal_pair

#填表法
def file_table():
    global mini_DFA,pre_DFA,equal_pair
    #首先将接受状态区分开
    for state1 in pre_DFA['state']:
        for state2 in pre_DFA['state']:
            if state1 < state2 and (pre_DFA['state'][state1]['is_final'] != pre_DFA['state'][state2]['is_final']):
                equal_pair.remove([state1, state2])
    #循环到没有改变为止，填表结束
    not_change = True
    while 1:
        not_change = True
        for state1 in pre_DFA['state']:
            for state2 in pre_DFA['state']:
                #未区分过的前大后小对
                if state1 < state2 and [state1,state2] in equal_pair:
                    for input_str in pre_DFA['input']:
                        temp1 = pre_DFA['state'][state1]['transition'][input_str]
                        temp2 = pre_DFA['state'][state2]['transition'][input_str]
                        if not ([temp1,temp2] in equal_pair or [temp2,temp1] in equal_pair) and temp1 != temp2:
                            not_change = False
                            equal_pair.remove([state1, state2])
                            break
        if not_change:
            break
    #归并等价对
    while 1:
        not_change = True
        for i in range(len(equal_pair)-1):
            for j in range(i+1, len(equal_pair)):
                #合集长度小于两个长度之和，则有重叠部分，
                #由等价传递性，两集合内所有点均等价
                temp = list(set(equal_pair[i])|set(equal_pair[j]))
                if len(equal_pair[i])+len(equal_pair[j]) > len(temp):
                    del equal_pair[i]
                    del equal_pair[j-1]
                    equal_pair.append(temp)
                    not_change = False
                    break
            if not not_change:
                break
        if not_change:
            break
    #将剩下单独成组的元素加入
    for state in pre_DFA['state']:
        not_exist= True
        for equal in equal_pair:
            if state in equal:
                not_exist = False
        if not_exist:
            equal_pair.append([state])
    #print equal_pair


#equal_pair = [[1,4],[2,5],[5,8],[1,7],[3,6],[4,7],[2,8]]
#利用填好的表格重建DFA
def rebuild_NDA():
    global mini_DFA,pre_DFA,equal_pair
    #mini_DFA的input
    mini_DFA['input'] = pre_DFA['input']
    #对final，start赋值
    for i in range(len(equal_pair)):
        state_name = 'Q' + str(i)
        temp = {
            'name':'',
            'is_start':False,
            'is_final':False,
            'transition':{
            }
        }
        mini_DFA['state'][state_name] = temp
        #name
        equal_pair[i].sort()
        mini_DFA['state'][state_name]['name'] = ('_').join(equal_pair[i])
        #是否为初态或终态
        for state in equal_pair[i]:
            if pre_DFA['state'][state]['is_start']:
                mini_DFA['state'][state_name]['is_start'] = True
                mini_DFA['start'] = state_name
            if pre_DFA['state'][state]['is_final']:
                mini_DFA['state'][state_name]['is_final'] = True
                mini_DFA['final'].append(state_name)

        #添加transition
        for input_str in mini_DFA['input']:
            #if not [state1['transition'][input_str],state2['transition'][input_str]] in equal_pair:
                #equal_pair.remove([state1, state2])
            for s in range(len(equal_pair)):
                if pre_DFA['state'][equal_pair[i][0]]['transition'][input_str] in equal_pair[s]:
                    #如果出现在s处，则指向s
                    mini_DFA['state'][state_name]['transition'][input_str] = 'Q' + str(s)
                    break