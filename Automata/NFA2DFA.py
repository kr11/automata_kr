#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
import datetime
import json
from django.shortcuts import render_to_response
from django.utils import simplejson
#test样例，json格式
NFA = {
        'type':'NFA',
        'state':{
            'q0':{
                'name':'q0',
                'isStart':True,
                'isFinal':False,
                'transition':{
                    'null':['q1'],
                    '+':['q1'],
                }
            },
             'q1':{
                'name':'q1',
                'isStart':False,
                'isFinal':False,
                'transition':{
                    '.':['q2'],
                    '0':['q1','q4'],
                }
            },
             'q2':{
                'name':'q2',
                'isStart':False,
                'isFinal':False,
                'transition':{
                    '0':['q3'],
                }
            },
             'q3':{
                'name':'q3',
                'isStart':False,
                'isFinal':False,
                'transition':{
                    'null':['q5'],
                    '0':['q3'],
                }
            },
             'q4':{
                'name':'q4',
                'isStart':False,
                'isFinal':False,
                'transition':{
                    '.':['q3'],
                }
            },
             'q5':{
                'name':'q5',
                'isStart':False,
                'isFinal':True,
                'transition':{
                }
            },
        },
        'input':['0','.','+','null'],
        'startState':'q0',
        'finalState':['q5'],
    }

new_state_count = 0#转化DFA得到的新状态个数（用于命名新的）
add_new_state = {}#已经重命名过的新状态，对应他的新名字
DFA = {} #待返回的DFA结构体


#✘✘✘获取空闭集，返回一个字符串，
#获取空闭集，返回一个字典，
def get_null_set(start_state):
    global NFA,DFA,new_state_count,add_new_state
<<<<<<< HEAD
    state_array = start_state
    #state_array = start_state.split('_')
=======
    #state_array = start_state.split('_')
    state_array = start_state
>>>>>>> 744d83408d34e57e9abcad1211991cb017d1a3cc
    while 1:
        not_change = True
        for state in state_array:
            #如果添加之后长度变化则有新的进入
            if state != '' and u'ε'in NFA['state'][state]['transition']:
                pre_len = len(state_array)
<<<<<<< HEAD
                null_state = NFA['state'][state]['transition']['null'] #.split('_')
=======
                null_state = NFA['state'][state]['transition'][u'ε'] #.split('_')
>>>>>>> 744d83408d34e57e9abcad1211991cb017d1a3cc
                state_array = list(set(state_array) | set(null_state))
                now_len = len(state_array)
                if pre_len != now_len:
                    not_change = False
                    break
        if not_change:
            break
    state_array.sort()
    return '_'.join(state_array), state_array


#NFA转DFA函数
def NFA2DFA(request):
    global NFA,DFA,new_state_count,add_new_state
<<<<<<< HEAD
    #NFA来自于前端的信息转化
    #NFA = simplejson.loads(request.raw_post_data)
=======
    #NFA = json.loads(request.body)
    #pre_DFA = simplejson.loads(request.raw_post_data)
>>>>>>> 744d83408d34e57e9abcad1211991cb017d1a3cc
    retransition(init_NFA2DFA())
    dfa_json = json.dumps(DFA)
    #print dfa_json
     #json=simplejson.dumps(mini_DFA)
    return HttpResponse(dfa_json)

def init_NFA2DFA():
    global NFA,DFA,new_state_count,add_new_state
    new_state_count = 0
    add_new_state = {}
    DFA = {
        'type':'DFA',
        'state':{
        },
        'input':[],
        'startState':'',
        'finalState':[],
    }
    DFA['input'] = NFA['input']
    #去掉null
    if u'ε' in DFA['input']:
        DFA['input'].remove(u'ε')
    #处理初始状态，开始retran递归
    #初始状态格式为q0，闭包的格式为q1_12,直接q0+闭包即可
    #null_state = NFA['state']['startState']['transition']['null'].split('_')
    temp = {
            'name':'',
            'isStart':False,
            'isFinal':False,
            'transition':{
            }
        }
    #新的名字new_name与原组成状态new_start
<<<<<<< HEAD
    new_start = NFA['start']
    #newname：DFA中新状态的序号（名字）
    #temp：状态模板
=======
    new_start = NFA['startState']

>>>>>>> 744d83408d34e57e9abcad1211991cb017d1a3cc
    new_name = 'Q'+str(new_state_count)
    DFA['state'][new_name] = temp
    DFA['state'][new_name]['isStart'] = True

    #if 'null' in NFA['state'][new_start]['transition']:
    #    new_start += NFA['state'][new_start]['transition']['null']

    #注意，name不参与各种判断，他只是记录这个新状态是由以前的什么状态组成的
    #name = state + ‘_’ + state
    new_start, null_state = get_null_set([new_start])
    DFA['state'][new_name]['name'] = new_start

    #判断start
    DFA['startState'] = new_name
    #DFA['start'] = new_name
    #判断final
    #null_state = new_start.split('_')
    for state in null_state:
        if state != '' and NFA['state'][state]['isFinal']:
            DFA['state']['Q'+str(new_state_count)]['isFinal'] = True

    add_new_state[new_start] = new_state_count
    new_state_count += 1
    #return new_start
    return null_state


#递归查找，重新划分转移函数
#输入为待查找的状态名
def retransition(state_name):
    global NFA,DFA,new_state_count,add_new_state
    #将该状态包含的原始状态划分开
    state_array = state_name #.split('_')#本次字符串包含的状态
    #依次寻找能到达的状态放入temp_state中
    for input_str in DFA['input']:
        #各输入条件
        next_state = []#本次转移将要到达的新状态
        for state in state_array:
            #各状态的本次转移结果均添加入next_state
<<<<<<< HEAD
            if state != '' and input_str in NFA['state'][state]['transition']:
                temp_state = NFA['state'][state]['transition'][input_str]#.split('_')
=======
            if (state != '') and input_str in NFA['state'][state]['transition']:
                temp_state = NFA['state'][state]['transition'][input_str] #.split('_')
>>>>>>> 744d83408d34e57e9abcad1211991cb017d1a3cc
            #if temp_state != '':
                next_state = list(set(next_state) | set(temp_state))
            #if
            #    next_state.remove('')

        #对得到的next_state求空闭集

        #for state in next_state:
        #    if (state != '') and (u'ε' in NFA['state'][state]['transition']):
        #        null_state = NFA['state'][state]['transition'][u'ε'] #.split('_')
        #        next_state = list(set(next_state) | set(null_state))

        #现在得到了新的一个集合，放入add_new_state
        #next_state.sort()
        #new_state_name = '_'.join(next_state)

        new_state_name, next_state = get_null_set(next_state)#('_'.join(next_state))

        #若还未出现过，开始递归调用,否则只是添加转移
        if not (new_state_name in add_new_state):
            #添加state
            temp = {
                'name':'',
                'isStart':False,
                'isFinal':False,
                'transition':{
                }
            }
            #新的名字与原组成状态
            new_name = 'Q'+str(new_state_count)
            DFA['state'][new_name] = temp
            DFA['state'][new_name]['name'] = new_state_name

            #判断final
            for state in next_state:
                if state != '' and NFA['state'][state]['isFinal']:
                    DFA['state']['Q'+str(new_state_count)]['isFinal'] = True
                    DFA['finalState'].append('Q'+str(new_state_count))

            add_new_state[new_state_name] = new_state_count
            new_state_count += 1
            #递归调用
            retransition(next_state)

        #给上一层添加转移state_name
<<<<<<< HEAD
        DFA['state']['Q'+ str(add_new_state['_'.join(state_name)])]['transition'][input_str] = ['Q'+ str(add_new_state[new_state_name])]
=======
        DFA['state']['Q'+ str(add_new_state[state_name])]['transition'][input_str] = ['Q'+ str(add_new_state[new_state_name])]
>>>>>>> 744d83408d34e57e9abcad1211991cb017d1a3cc
