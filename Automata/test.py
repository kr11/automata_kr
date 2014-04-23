#encoding: utf-8
__author__ = 'manman'

from django.http import HttpResponse
import json
#test������json��ʽ
NFA ={
        'type':'NFA',           #�Զ�������
        'input':['0','1'],     #�Զ���������ż�
        'state':{               #�Զ���״̬����
            'q0':{
                'name':'q0',    #״̬��
                'isStart':True, #�Ƿ�Ϊ��ʼ״̬
                'isFinal':False,#�Ƿ�Ϊ�ս�״̬
                'transition':{  #ת�ƺ���
                    '0':['q0','q1'],#��������ת�ƽ��
                    '1':'q0',
                }
            },
        },
        'startState':'q0',      #��ʼ״̬
        'finalState':['q2'],    #��̬����
    }

new_state_count = 0#ת��DFA�õ�����״̬���������������µģ�
add_new_state = {}#�Ѿ�������������״̬����Ӧ����������
DFA = {} #�����ص�DFA�ṹ��



def get_null_set(start_state):
    global NFA,DFA,new_state_count,add_new_state
    state_array = start_state.split('_')
    while 1:
        not_change = True
        for state in state_array:
            if state != '' and u'��' in NFA['state'][state]['transition']:
                pre_len = len(state_array)
                null_state = NFA['state'][state]['transition'][u'��'] #.split('_')
                state_array = list(set(state_array) | set(null_state))
                now_len = len(state_array)
                if pre_len != now_len:
                    not_change = False
                    break
        if not_change:
            break
    state_array.sort()
    return '_'.join(state_array), state_array

#NFAתDFA����
def NFA2DFA(request):
    global NFA,DFA,new_state_count,add_new_state
    NFA = json.loads(request.body)
    retransition(init_NFA2DFA())
    dfa_json = json.dumps(DFA)
    #print dfa_json
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
    #ȥ��null
    if u'��' in DFA['input']:
        DFA['input'].remove(u'��')
    #�����ʼ״̬����ʼretran�ݹ�
    #��ʼ״̬��ʽΪq0���հ��ĸ�ʽΪq1_12,ֱ��q0+�հ�����
    #null_state = NFA['state']['startState']['transition']['null'].split('_')
    temp = {
            'name':'',
            'isStart':False,
            'isFinal':False,
            'transition':{
            }
        }
    #�µ�����new_name��ԭ���״̬new_start
    new_start = NFA['startState']

    new_name = 'Q'+str(new_state_count)
    DFA['state'][new_name] = temp
    DFA['state'][new_name]['isStart'] = True

    #if 'null' in NFA['state'][new_start]['transition']:
    #    new_start += NFA['state'][new_start]['transition']['null']
    new_start, null_state = get_null_set(new_start)
    DFA['state'][new_name]['name'] = new_start

    DFA['startState'] = new_name
    #null_state = new_start.split('_')
    #�ж�final
    for state in null_state:
        if state != '' and NFA['state'][state]['isFinal']:
            DFA['state']['Q'+str(new_state_count)]['isFinal'] = True

    add_new_state[new_start] = new_state_count
    new_state_count += 1
    return new_start

#�ݹ���ң����»���ת�ƺ���
#����Ϊ�����ҵ�״̬��
def retransition(state_name):
    global NFA,DFA,new_state_count,add_new_state
    #����״̬������ԭʼ״̬���ֿ�
    state_array = state_name.split('_')#�����ַ���������״̬
    #����Ѱ���ܵ����״̬����temp_state��
    for input_str in DFA['input']:
        #����������
        next_state = []#����ת�ƽ�Ҫ�������״̬
        for state in state_array:
            #��״̬�ı���ת�ƽ���������next_state
            if (state != '') and input_str in NFA['state'][state]['transition']:
                temp_state = NFA['state'][state]['transition'][input_str] #.split('_')
            #if temp_state != '':
                next_state = list(set(next_state) | set(temp_state))
            #if
            #    next_state.remove('')

        #�Եõ���next_state��ձռ�
        #for state in next_state:
        #    if (state != '') and (u'��' in NFA['state'][state]['transition']):
        #        null_state = NFA['state'][state]['transition'][u'��'] #.split('_')
        #        next_state = list(set(next_state) | set(null_state))

        #���ڵõ����µ�һ�����ϣ�����add_new_state
        #next_state.sort()
        #new_state_name = '_'.join(next_state)

        new_state_name, next_state = get_null_set('_'.join(next_state))
        #����δ���ֹ�����ʼ�ݹ����,����ֻ�����ת��
        if not (new_state_name in add_new_state):
            #���state
            temp = {
                'name':'',
                'isStart':False,
                'isFinal':False,
                'transition':{
                }
            }
            #�µ�������ԭ���״̬
            new_name = 'Q'+str(new_state_count)
            DFA['state'][new_name] = temp
            DFA['state'][new_name]['name'] = new_state_name

            #�ж�final
            for state in next_state:
                if state != '' and NFA['state'][state]['isFinal']:
                    DFA['state']['Q'+str(new_state_count)]['isFinal'] = True
                    DFA['finalState'].append('Q'+str(new_state_count))

            add_new_state[new_state_name] = new_state_count
            new_state_count += 1
            #�ݹ����
            retransition(new_state_name)

        #����һ�����ת��state_name
        DFA['state']['Q'+ str(add_new_state[state_name])]['transition'][input_str] = ['Q'+ str(add_new_state[new_state_name])]
