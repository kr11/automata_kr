#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from Automata.NFA2DFA import *
from Automata.simplifyCFG import *
import copy
#test样例，json格式


CFG = {
        'type':'CFG',
        'Variable':['S','A','B','C'],
        'Terminal':['a','b'],
        'Start':'S',
        'pre_Production':{
            'S':'AB|BC',
            'A':'BA|a',
            'B':'CC|b',
            'C':'AB|a'
        },
        'final_Production':{
            #'S':[['i','S','S'],['e']],
        }
    }

judgeString = 'baaba'
#存放每次去除空产生式后的结果
temp_product = []

def CYKAlgorithm(CFG,judgeString):
    if CFG['final_Production'] == {}:
        CFG = parse_finalP(CFG)
    CFG = CFGsimplify(CFG)
    m_len = len(judgeString)+1
    CFG_product = CFG['final_Production']
    CYK_table = [[[] for i in range(m_len)] for s in range(m_len)]
    #填入字符串在X0i
    #for i in range(1,m_len):
    #    CYK_table[0][i] = judgeString[i]
    #计算第一行成员
    for i in range(1,m_len):
        temp = []
        for fore in CFG_product:
            for str_list in CFG_product[fore]:
                if str_list == [judgeString[i-1]] and fore not in temp:
                    temp.append(fore)
        CYK_table[i][i] = copy.deepcopy(temp)
    #计算之后的几行成员
    for row in range(2,m_len):
        for column in range(1,m_len-row+1):
            #改成员采取不同地方的切断
            temp = []
            for k in range(column,column + row - 1):
                #寻找是否会有这样的产生式
                for state1 in CYK_table[column][k]:
                    for state2 in CYK_table[k+1][column+ row -1]:
                        #如果有产生式A-->st1,st2，将A加入temp
                        for fore in CFG_product:
                            for str_list in CFG_product[fore]:
                                if str_list == [state1,state2] and fore not in temp:
                                    temp.append(fore)
            CYK_table[column][column+row-1] = copy.deepcopy(temp)
    if CYK_table[1][m_len-1] == []:
        return False
    else:
        return True

def fore_judgeCFG(request):
    global CFG,judgeString
    #CFG = simplejson.loads(request.raw_post_data)
    CYKAlgorithm(CFG,judgeString)
    #CFG = connnect_preP(CFG)
    #json=simplejson.dumps(CFG)
    return HttpResponse(CYKAlgorithm(CFG,judgeString))


