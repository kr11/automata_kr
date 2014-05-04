#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.utils import simplejson
import copy

DFA = {
        'type':'NFA',
        'state':{
            'A':{
                'name':'A',
                'is_start':True,
                'is_final':False,
                'transition':{
                    '0':['A'],
                    '1':['A','B'],
                }
            },
             'B':{
                'name':'q1',
                'is_start':False,
                'is_final':False,
                'transition':{
                    '0':['C'],
                    '1':['C'],
                }
             },
             'C':{
                'name':'C',
                'is_start':False,
                'is_final':True,
                'transition':{
                    '0':['D'],
                    '1':['D'],
                }
            },
             'D':{
                'name':'D',
                'is_start':False,
                'is_final':True,
                'transition':{
                }
            },
        },
        'input':['0','1',],
        'start':'A',
        'final':['C','D'],
    }
state_alias = []
table = []
pri_table = []
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
    global state_alias,pri_table,start_state,final_state

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
    state_alias = ['A','B','C','D']
    start_state = 0
    final_state = [2,3]
    #构建table
    pri_table = [['' for i in range(state_num)] for j in range(state_num)]
    #添加初始k = 0时候的转移
    for i in range(state_num):
        for j in range(state_num):
            trans = trans0(i,j,DFA,state_alias)
            if len(trans) == 0:
                pri_table[i][j] = '($)'
            else:
                pri_table[i][j] = '('+'+'.join(trans)+')'
            #if i != j:
            #    if len(trans) == 0:
            #        pri_table[i][j] = '($)'
            #    else:
            #        pri_table[i][j] = '('+'+'.join(trans)+')'
            #else:
                #将空转移加入
            #    if u'ε' not in trans:
            #        trans = [u'ε'] + trans
            #    pri_table[i][j] = '('+'+'.join(trans)+')'


#返回Rij + Rik(Rkk)*Rkj并化简
def route(i,j,k):
    global table
    Rij = table[i][j][1:-1]
    Rik = table[i][k][1:-1]
    Rkk = table[k][k][1:-1]
    Rkj = table[k][j][1:-1]
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

#计算R*SU*形式的正则表达式并返回
def star_cat_star(R,S,U):
    R = R[1:-1]
    S = S[1:-1]
    U = U[1:-1]
    if S == '$':
        return '$'
    elif R == '$' or U == '$':
        if R == '$' or R == u'ε':
            R = ''
        elif R[0] == u'ε':
            R = R[2:len(R)]
        if U == '$' or U == u'ε':
            U = ''
        elif R[0] == u'ε':
            U = U[2:len(U)]
        #处理S
        if S == u'ε':
            S = ''
        elif S == u'ε+' + R or S == u'ε+' + U:
            S = ''
        #处理U
        if S == '' and U == R:
            U == ''
        elif len(U) == 1:
            U = U + '*'
        elif len(U) > 1:
            U = '(' + U + ')*'
        #处理R
        if len(R) == 1:
            R = R + '*'
        elif len(R) > 1:
            R = '(' + R + ')*'
        #处理S
        if len(S) > 1:
            S = '(' + S + ')'
        if R+S+U == '':
            return u'(ε)'
        return  '(' + R + S + U + ')'
    if R == S == U == u'ε':
        return u'(ε)'
    #化简，此时str2不为$或者全空
    #处理R
    if R == u'ε':
        R = ''
    elif R[0] == u'ε':
        R = R[2:len(R)]
    if U == u'ε':
        U = ''
    elif R[0] == u'ε':
        U = U[2:len(U)]
    #处理S
    if S == u'ε':
        S = ''
    elif S == u'ε+' + R or S == u'ε+' + U:
        S = ''
    #处理U
    if S == '' and U == R:
        U == ''
    elif len(U) == 1:
        U = U + '*'
    elif len(U) > 1:
        U = '(' + U + ')*'
    #处理R
    if len(R) == 1:
        R = R + '*'
    elif len(R) > 1:
        R = '(' + R + ')*'
    #处理S
    if len(S) > 1:
        S = '(' + S + ')'
    return  '(' + R + S + U + ')'

#处理Rss*化简并返回
def star_string(Rss):
    Rss = Rss[1:-1]
    if Rss == '$':
        return u'(ε)'
    if Rss == u'ε':
        return u'(ε)'
    #化简，此时Rss不为$或者全空
    #处理Rss
    if Rss[0] == u'ε':
        R = Rss[2:len(Rss)]
    #设置Rss
    if len(Rss) == 1:
        R = R + '*'
    elif len(Rss) > 1:
        R = '(' + Rss + ')*'
    return  '(' +  Rss + ')'


def DFA2RE_state(DFA):
    global start_state,final_state,table,pri_table
    #初始化，赋予每个状态别名，将k = 0时的所有转移算出
    init_table(DFA)
    #route迭代
    state_num = len(DFA['state'])
    #存放不同终态的结果
    RE_result = []
    #以下循环中均为数字（状态别名）
    for f_st in final_state:
        #已经删除的状态，每个终态开始循环时清空
        rmv_state = []
        table = copy.deepcopy(pri_table)
        for to_rmv_st in range(state_num):#to_rmv_st待删除状态
            if to_rmv_st != start_state \
                and to_rmv_st != f_st \
                and to_rmv_st not in rmv_state:
                rmv_state.append(to_rmv_st)
                for state1 in range(state_num):
                    for state2 in range(state_num):
                        if state1 not in rmv_state and state2 not in rmv_state:
                            res = route(state1,state2,to_rmv_st)
                            table[state1][state2] = res
        #所有非初始终结状态均删除，得到结果：
        temp_string = ''
        if f_st != start_state:
            temp1 = route(start_state,start_state,f_st)
            temp_string = star_cat_star(temp1,table[start_state][f_st],table[f_st][f_st])
        else:
            temp_string = star_string(table[f_st][f_st])
        if temp_string not in RE_result:
            RE_result.append(temp_string)
    #合并
    if '$' in RE_result and len(RE_result) > 1:
        RE_result.remove('$')
    for var in RE_result:
        var = var[1:-1]
    return '+'.join(RE_result)


#路径迭代法
def fore_DFA2RE_state(request):
    global DFA
    #DFA = simplejson.loads(request.raw_post_data)
    REstring = DFA2RE_state(DFA)
    #如果是空语句
    return HttpResponse(REstring)