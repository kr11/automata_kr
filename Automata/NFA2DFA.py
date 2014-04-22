#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
import datetime
from django.shortcuts import render_to_response
from django.utils import simplejson
#test样例，json格式

NFA = {
        'type':'NFA',
        'state':{
            'q0':{
                'name':'q0',
                'is_start':True,
                'is_final':False,
                'transition':{
                    'null':'q1',
                    '+':'q1',
                }
            },
             'q1':{
                'name':'q1',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '.':'q2',
                    '0':'q1_q4',
                }
            },
             'q2':{
                'name':'q2',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':'q3',
                }
            },
             'q3':{
                'name':'q3',
                'is_start':False,
                'is_final':False,
                'transition':{
                    'null':'q5',
                    '0':'q3',
                }
            },
             'q4':{
                'name':'q4',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '.':'q3',
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
        'input':['0','.','+','null'],
        'start':'q0',
        'final':['q5'],
    }

new_state_count = 0#转化DFA得到的新状态个数（用于命名新的）
add_new_state = {}#已经重命名过的新状态，对应他的新名字
DFA = {} #待返回的DFA结构体


#获取空闭集，返回一个字符串，
# 由闭集的状态间隔‘_’组成
def get_null_set(start_state):
    global NFA,DFA,new_state_count,add_new_state
    state_array = start_state.split('_')
    while 1:
        not_change = True
        for state in state_array:
            #如果添加之后长度变化则有新的进入
            if state != '' and 'null' in NFA['state'][state]['transition']:
                pre_len = len(state_array)
                null_state = NFA['state'][state]['transition']['null'].split('_')
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
    #NFA = simplejson.loads(request.raw_post_data)
    retransition(init_NFA2DFA())
    json=simplejson.dumps(DFA)
    return HttpResponse(json)

def init_NFA2DFA():
    global NFA,DFA,new_state_count,add_new_state
    new_state_count = 0
    add_new_state = {}
    DFA = {
        'type':'DFA',
        'state':{
        },
        'input':[],
        'start':'',
        'final':[],
    }
    DFA['input'] = NFA['input']
    #去掉null
    if 'null' in DFA['input']:
        DFA['input'].remove('null')
    #处理初始状态，开始retran递归
    #初始状态格式为q0，闭包的格式为q1_12,直接q0+闭包即可
    #null_state = NFA['state']['start']['transition']['null'].split('_')
    temp = {
            'name':'',
            'is_start':False,
            'is_final':False,
            'transition':{
            }
        }
    #新的名字new_name与原组成状态new_start
    new_start = NFA['start']

    new_name = 'Q'+str(new_state_count)
    DFA['state'][new_name] = temp
    DFA['state'][new_name]['is_start'] = True

    #if 'null' in NFA['state'][new_start]['transition']:
    #    new_start += NFA['state'][new_start]['transition']['null']
    new_start, null_state = get_null_set(new_start)
    DFA['state'][new_name]['name'] = new_start

    #判断start
    DFA['start'] = new_name
    #判断final
    #null_state = new_start.split('_')
    for state in null_state:
        if state != '' and NFA['state'][state]['is_final']:
            DFA['state']['Q'+str(new_state_count)]['is_final'] = True

    add_new_state[new_start] = new_state_count
    new_state_count += 1
    return new_start


#递归查找，重新划分转移函数
#输入为待查找的状态名
def retransition(state_name):
    global NFA,DFA,new_state_count,add_new_state
    #将该状态包含的原始状态划分开
    state_array = state_name.split('_')#本次字符串包含的状态
    #依次寻找能到达的状态放入temp_state中
    for input_str in DFA['input']:
        #各输入条件
        next_state = []#本次转移将要到达的新状态
        for state in state_array:
            #各状态的本次转移结果均添加入next_state
            if state != '' and input_str in NFA['state'][state]['transition']:
                temp_state = NFA['state'][state]['transition'][input_str].split('_')
            #if temp_state != '':
                next_state = list(set(next_state) | set(temp_state))
            #if
            #    next_state.remove('')

        #对得到的next_state求空闭集

        #for state in next_state:
        #    if (state != '') and ('null' in NFA['state'][state]['transition']):
        #        null_state = NFA['state'][state]['transition']['null'].split('_')
        #        next_state = list(set(next_state) | set(null_state))

        #现在得到了新的一个集合，放入add_new_state
        #next_state.sort()
        #new_state_name = '_'.join(next_state)

        new_state_name, next_state = get_null_set('_'.join(next_state))

        #若还未出现过，开始递归调用,否则只是添加转移
        if not (new_state_name in add_new_state):
            #添加state
            temp = {
                'name':'',
                'is_start':False,
                'is_final':False,
                'transition':{
                }
            }
            #新的名字与原组成状态
            new_name = 'Q'+str(new_state_count)
            DFA['state'][new_name] = temp
            DFA['state'][new_name]['name'] = new_state_name

            #判断final
            for state in next_state:
                if state != '' and NFA['state'][state]['is_final']:
                    DFA['state']['Q'+str(new_state_count)]['is_final'] = True
                    DFA['final'].append('Q'+str(new_state_count))

            add_new_state[new_state_name] = new_state_count
            new_state_count += 1
            #递归调用
            retransition(new_state_name)

        #给上一层添加转移state_name
        DFA['state']['Q'+ str(add_new_state[state_name])]['transition'][input_str] = 'Q'+ str(add_new_state[new_state_name])
