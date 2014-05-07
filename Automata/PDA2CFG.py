#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from Automata.convertNP_LP import *
from django.shortcuts import render_to_response
import copy
#test样例，json格式

PDA = {
        'type':'PDA',
        'receive':'empty',
        'input':['i','e'],
        'stack_input':['Z'],
        'start_state':'q',
        'start_stack':'Z',
        'stack':['Z'],
        'final':[],
        'state':{
            'q':{
                'name':'q',
                'is_start':True,
                'is_final':False,
                'transition':{
                    'i':{
                        'Z':[['q',['Z','Z']],],
                    },
                     'e':{
                        'Z':[['q',[u'ε']],],
                    },
                }
            },
        },
    }
#上下无关文法
CFG = {
        'type':'CFG',
        'Variable':['S'],
        'Terminal':['i','e'],
        'Start':'S',
        'pre_Production':{
            'S':'iSS|e'
        },
        'final_Production':{
            'S':[['i','S','S'],['e']],
        }
    }

#将拆开的final_Production连接成pre_Production
def connnect_preP(CFG):
    for fore in CFG['final_Production']:
        #CFG['pre_Production'][fore] = ''
        temp = []
        for trans in CFG['final_Production'][fore]:
            temp.append(''.join(trans))
        CFG['pre_Production'][fore] = '|'.join(temp)
            #CFG['pre_Production'][fore] += ''.join(trans)
    return CFG

#将连在一起的pre_Production拆分成final_Production
def parse_finalP(CFG):
    for fore in CFG['pre_Production']:
        product = CFG['pre_Production'][fore].split('|')
        index = 0
        CFG['final_Production'][fore] = []
        for per_pro in product:
            if per_pro == u'ε':
                CFG['final_Production'][fore].append([u'ε'])
                continue
            #将每个连起来的串分割成有终结符或变元组成的数组
            temp = parsePro(per_pro,CFG['Variable'],CFG['Terminal'])
            if temp == []:
                return [] #[]说明出错，返回
            else:
                CFG['final_Production'][fore].append(temp)

    return CFG

def parsePro(per_pro,Var,Ter):
    list = []
    #当前扫描位置
    index = 0
    #终结符
    while(index < len(per_pro)):
        iffound = False
        for i in range(index+1,len(per_pro)+1):
            temp = per_pro[index:i]
            if temp in Var or temp in Ter:
                index = i
                list.append(temp)
                iffound = True
                break

            if iffound == False:
                return []
    return list

#初始化add_new_state，将所有[qXp]编号，放入
def number_addNewState(PDA):
    Variable = []
    num = 0
    for i in PDA['stack_input']:
        for s in PDA['state']:
            for r in PDA['state']:
                add_new_state[s+i+r] = num
                Variable.append('Q'+str(num))
                num += 1
    return Variable

add_new_state = {}#已经重命名过的新状态，对应他的新名字

def turn_to_var(m_str):
    global add_new_state
    return 'Q' + str(add_new_state[m_str])
#NFA转DFA函数
def PDA2CFG(request):
    global PDA,CFG
    #从前端得到FA和judgeString的值
    #PDA = simplejson.loads(request.raw_post_data)

    new_state_count = 0   #下一次添加状态‘Q’+ new_state_count
    temp = ''
    #初始化CFG
    CFG = {
        'type':'CFG',
        'Variable':['S'],
        'Terminal':[],
        'Start':'S',
        'pre_Production':{
        },
        'final_Production':{
        }
    }

    #初始化add_new_state，将所有[qXp]编号，放入
    CFG['Variable'] = number_addNewState(PDA)
    CFG['final_Production']['S'] = []
    #加入初始状态
    for state in PDA['state']:
        temp = PDA['start_state']+PDA['start_stack']+state
        CFG['final_Production']['S'].append([turn_to_var(temp)])
    #不断加入所有的转移状态
    for state in PDA['state']:
        for m_input in PDA['state'][state]['transition']:
            for m_stack in PDA['state'][state]['transition'][m_input]:
                #每一个结果序对
                for result in PDA['state'][state]['transition'][m_input][m_stack]:
                    k = len(result[1])
                    if result[1] == [u'ε']:
                        k = 0
                    #qXrk的每一种情况
                    for rk in PDA['state']:
                        temp = turn_to_var(state + m_stack + rk)
                        if temp not in CFG['final_Production']:
                            CFG['final_Production'][temp] = []
                        if m_input == [u'ε']:
                            per_production(PDA,temp,result[0],result[1],rk,[],k)
                        else:
                            CFG['Terminal'].append(m_input)
                            per_production(PDA,temp,result[0],result[1],rk,[m_input],k)

    CFG = connnect_preP(CFG)
    json=simplejson.dumps(CFG)
    return HttpResponse(json)

#到达k之后
#PDA:；fore：待添加的产生式前半部分；fore_r:三部分的第一部分，与上一段同
#stack：数组stack
# product：数组，不断添加删除；k：迭代步骤
#rk：最后的结尾，k=1时添加
def per_production(PDA,fore,fore_r,stack,rk,product,k):
    global CFG
    #完毕
    if k == 0:
        #只有在栈转移是X/ε的情况下才会出现
        #temp = copy.deepcopy(product)
        if product == []:  #输入也为ε，则转移表达式为Q0-->ε
            product = [u'ε']
        CFG['final_Production'][fore].append(product)
        return
    #一种产生式结束，添加
    if k == 1:
        product.append(turn_to_var(fore_r + stack[-k] + rk))
        temp = copy.deepcopy(product)
        CFG['final_Production'][fore].append(temp)
        product.pop()
        return

    #依次加入所有的状态，进入下一级
    for state in PDA['state']:
        product.append(turn_to_var(fore_r + stack[-k] + state))
        per_production(PDA,fore,state,stack,rk,product,k-1)
        product.pop()
