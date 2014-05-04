#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson

DFA = {
        'type':'DFA',
        'state':{
            'q0':{
                'name':'q0',
                'is_start':True,
                'is_final':False,
                'transition':{
                    '0':['q1'],
                    '1':['q0'],
                }
            },
             'q1':{
                'name':'q1',
                'is_start':False,
                'is_final':True,
                'transition':{
                    '0':['q1'],
                    '1':['q1'],
                }
             }
        },
        'input':['0','1',],
        'start':'q0',
        'final':['q1'],
    }
state_alias = []
table = []
start_state = 0 #记录初始状态的序号
final_state = [] #记录终结状态的序号集合
def trans0(i,j,DFA,state_alias):
    ret = []
    for input in DFA['input']:
        if state_alias[i] in DFA['state']\
                and input in DFA['state'][state_alias[i]]['transition']\
                and state_alias[j] in DFA['state'][state_alias[i]]['transition'][input]:
            ret.append(input)
    return ret
def init_table(DFA):
    global state_alias,table,start_state,final_state

    state_num = len(DFA['state'])
    #为每一个状态取别名
    state_alias = ['' for i in range(state_num)]
    i = 0
    for state in DFA['state']:
        if state == DFA['start']:
            start_state = i
        if state in DFA['final']:
            final_state.append(i)
        state_alias[i] = state
        i += 1
    #state_alias = ['q0','q1']
    #start_state = 0
    #final_state = [1]
    #构建table
    table = [[['' for i in range(state_num)] for j in range(state_num)] for g in range(2)]
    #添加初始k = 0时候的转移
    for i in range(state_num):
        for j in range(state_num):
            trans = trans0(i,j,DFA,state_alias)
            if i != j:
                if len(trans) == 0:
                    table[0][i][j] = '($)'
                else:
                    table[0][i][j] = '('+'+'.join(trans)+')'
            else:
                #将空转移加入
                if u'ε' not in trans:
                    trans = [u'ε'] + trans
                table[0][i][j] = '('+'+'.join(trans)+')'



def route(pre,i,j,k):
    global table
    Rij = table[pre][i][j][1:-1]
    Rik = table[pre][i][k][1:-1]
    Rkk = table[pre][k][k][1:-1]
    Rkj = table[pre][k][j][1:-1]
    str1 = ''
    str2 = ''
    if Rij != '$':
        str1 = Rij
    #后三项
    if Rik == '$' or Rkj == '$':
        return '('+Rij+')'
    elif Rkk == '$':
        #Rkk*= u'ε'
        if Rik == Rkj == u'ε':
            str2 = u'ε'
            if str1 == '':
                return u'(ε)'
            elif str1[0] == u'ε':
                return '('+str1+')'
            else:
                return u'(ε' + str1 + ')'
        else:
            #化简，此时str2不为$或者全空
            #处理Rkk
            Rkk = ''
            #处理Rik
            if Rik == u'ε':
                Rik = ''
            else:
                Rik = '(' + Rik + ')'
            #处理Rkj
            if Rkj == u'ε':
                Rkj = ''
            else:
                Rkj = '(' + Rkj + ')'
            if Rkj == Rik:
                Rkj = ''
            #设置Rkk
            str2 = Rik + Rkk + Rkj
            #综合
            if str1 == '':
                return '(' + str2 +')'
            elif str1 == u'ε':
                if str2[0] == u'ε':
                    return  '(' + str2 + ')'
                else:
                    return  u'(ε+' + str2 + ')'
            elif str1[0] == u'ε' and len(str1) > 1:
                if str2[0] == u'ε':
                    str2 = str2[2:len(str2)]
                    return '(' + str1 + '+' + str2 + ')'
                else:
                    return '(' + str1 + '+' + str2 + ')'
            else:
                return '(' + str1 + '+' + str2 + ')'
    elif Rik == Rkk == Rkj == u'ε':
        str2 = u'ε'
        if str1 == '':
            return u'(ε)'
        elif str1[0] == u'ε':
            return '('+str1+')'
        else:
            return u'(ε' + str1 + ')'
    else:
        #化简，此时str2不为$或者全空
        #处理Rkk
        if Rkk == u'ε':
            Rkk = ''
        elif Rkk[0] == u'ε':
            Rkk = Rkk[2:len(Rkk)]
        #处理Rik
        if Rik == u'ε':
            Rik = ''
        elif Rik == u'ε+' + Rkk:
            Rik = ''
        #处理Rkj
        if Rkj == u'ε':
            Rkj = ''
        elif Rkj == u'ε+' + Rkk:
            Rkj = ''
        #设置Rkk
        if len(Rkk) == 1:
            Rkk = Rkk + '*'
        elif len(Rkk) > 1:
            Rkk = '(' + Rkk + ')*'
        if Rik != '':
            Rik = '(' + Rik + ')'
        if Rkk != '':
            Rkk = '(' + Rkk + ')'
        if Rkj != '':
            Rkj = '(' + Rkj + ')'
        str2 = Rik  + Rkk + Rkj
        #综合
        if str1 == '':
            return '(' + str2 +')'
        elif str1 == u'ε':
            if str2[0] == u'ε':
                return  '(' + str2 + ')'
            else:
                return  u'(ε+' + str2 + ')'
        elif str1[0] == u'ε' and len(str1) > 1:
            if str2[0] == u'ε':
                str2 = str2[2:len(str2)]
                return '(' + str1 + '+' + str2 + ')'
            else:
                return '(' + str1 + '+' + str2 + ')'
        else:
            return '(' + str1 + '+' + str2 + ')'

def DFA2RE_route(DFA):
    global start_state,final_state,table
    #初始化，赋予每个状态别名，将k = 0时的所有转移算出
    init_table(DFA)
    #route迭代
    state_num = len(DFA['state'])
    pre = 0
    for k in range(state_num):
        for i in range(state_num):
            for j in range(state_num):
                res = route(pre,i,j,k)
                table[1-pre][i][j] = res
        pre = 1-pre

    #结尾处理返回
    RE_result = []
    for final in final_state:
        temp = table[pre][start_state][final]
        if temp not in RE_result:
            RE_result.append(temp)
    if '$' in RE_result and len(RE_result) > 1:
        RE_result.remove('$')
    for var in RE_result:
        var = var[1:-1]
    #if len(RE_result) == 1:
    #    return RE_result[0][1:-1]
    return '+'.join(RE_result)


#路径迭代法
def fore_DFA2RE_route(request):
    global DFA
    #DFA = simplejson.loads(request.raw_post_data)
    REstring = DFA2RE_route(DFA)
    #如果是空语句
    return HttpResponse(REstring)