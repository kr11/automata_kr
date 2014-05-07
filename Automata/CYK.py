#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render_to_response
from Automata.PDA2CFG import *
import copy
#test样例，json格式

PDA = {
        'type':'PDA',
        'receive':'empty',
         'input':[],
         'stack_input':[],
        'start_state':'q0',
        'start_stack':'S',
        'stack':['S'],
        'final':['q0'],
        'state':{
            'q0':{
                'name':'q0',
                'is_start':True,
                'is_final':False,
                'transition':{
                }
            },
        }
    }
#上下无关文法
CFG = {
        'type':'CFG',
        'Variable':['I','E'],
        'Terminal':['a','b','0','1','(',')','+','*'],
        'Start':'E',
        'pre_Production':{
            'I':'a|b|Ia|Ib|I0|I1',
            'E':'I|E*E|E+E|(E)',
        },
        'final_Production':{
            #'S':[['i','S','S'],['e']],
        }
    }
CFG = {
        'type':'CFG',
        'Variable':['S','A','B'],
        'Terminal':['a','b'],
        'Start':'S',
        'pre_Production':{
            'S':'AB',
            'A':u'aAA|ε',
            'B':u'bBB|ε'
        },
        'final_Production':{
            #'S':[['i','S','S'],['e']],
        }
    }
CFG = {
        'type':'CFG',
        'Variable':['I','E','T','F'],
        'Terminal':['a','b','0','1','(',')','+','*'],
        'Start':'E',
        'pre_Production':{
            'I':'a|b|Ia|Ib|I0|I1',
            'F':'I|(E)',
            'T':'F|T*F',
            'E':'T|E+T',
        },
        'final_Production':{
            #'S':[['i','S','S'],['e']],
        }
    }
DFG = {
        'type':'CFG',
        'Variable':['S','A','B'],
        'Terminal':['a','b'],
        'Start':'S',
        'pre_Production':{
            'S':'AB|a',
            'A':'b'
        },
        'final_Production':{
            #'S':[['i','S','S'],['e']],
        }
    }
#存放每次去除空产生式后的结果
temp_product = []


#去除u'ε'产生式
def removeNull(CFG):
    global temp_product
    #去空
    #if_null_flag记录每一条产生式是否可空
    CFG_product = CFG['final_Production']
    if_null_flag = {}
    #终结符均不可空
    #0：不可空 1：可空；2：全空（只能产生）u'ε'
    for ter in CFG['Terminal']:
        if_null_flag[ter] = 0
    #变元
    for var in CFG['Variable']:
        if var not in CFG['final_Production']:
            return False
        #0：不可空 1：可空；2：全空（只能产生）u'ε'
        if [u'ε'] not in CFG['final_Production'][var]:
            if_null_flag[var] = 0
        elif len(CFG['final_Production'][var]) == 1:
            if_null_flag[var] = 2
        else:
            if_null_flag[var] = 1

    #逐个判断所有产生式
    for pre in CFG_product:
        temp = []
        #对每一个产生式
        for str_list in CFG_product[pre]:
            if str_list != [u'ε']:
                temp_product = []
                per_remove_null(str_list,0,[],if_null_flag)
                if temp_product == []:
                    return False
                temp += temp_product
        #将临时的temp覆盖原来的pre
        CFG['final_Production'][pre] = copy.deepcopy(temp)
    return CFG

#从原来的产生式产生新的不含空的产生式
#prod_list：产生式后半部分数组；index:当前要判断第几个,
## rmv_null_str:之前几步产生的产生式列表,if_null_flag:是否可空列表
def per_remove_null(prod_list,index,rmv_null_str,if_null_flag):
    global temp_product
    if index == len(prod_list):
        if rmv_null_str != [] and rmv_null_str not in temp_product:
            temp_product.append([])
            temp_product[-1] = copy.deepcopy(rmv_null_str)
        return
    if if_null_flag[prod_list[index]] == 0:#不可空
        rmv_null_str.append(prod_list[index])
        per_remove_null(prod_list,index+1,rmv_null_str,if_null_flag)
    elif if_null_flag[prod_list[index]] == 1:#可空
        #去掉可空的情况
        per_remove_null(prod_list,index+1,rmv_null_str,if_null_flag)
        rmv_null_str.append(prod_list[index])
        per_remove_null(prod_list,index+1,rmv_null_str,if_null_flag)
        rmv_null_str.pop()
    else:#绝对空
        per_remove_null(prod_list,index+1,rmv_null_str,if_null_flag)


def remove_unit_prod(CFG):
    #去单位产生式
    CFG_product = CFG['final_Production']
    unit_pair = []
    #加入零步单位对
    for var in CFG['Variable']:
        unit_pair.append([var,var])
    #加入其它单位对
    m_changed = True
    while m_changed:
        m_changed = False
        for pair in unit_pair:
            for pro in CFG_product[pair[1]]:
                if len(pro) == 1 and pro[0] in CFG['Variable'] and [pair[0],pro[0]] not in unit_pair:
                    unit_pair.append([pair[0],pro[0]])
                    m_changed = True

    #第二步
    temp = {}#temp变量存放新的去掉单位产生式的产生式集合
    for pair in unit_pair:
        if pair[0] not in temp:
            temp[pair[0]] = []
        for str_list in CFG_product[pair[1]]:
            if len(str_list) > 1 or (len(str_list) == 1 and str_list[0] in CFG['Terminal']):
                temp[pair[0]].append(str_list)
    CFG['final_Production'] = copy.deepcopy(temp)
    return CFG

#去除非产生式
def remove_notproduct(CFG):
    #if_null_flag记录每一条产生式是否可空
    CFG_product = copy.deepcopy(CFG['final_Production'])
    product_set = []
    #所有t都是可产生的
    for ter in CFG['Terminal']:
        product_set.append(ter)
    #找出所有产生符号
    m_changed = True
    while m_changed:
        m_changed = False
        for fore in CFG_product:
            if fore not in product_set:
                for str_list in CFG_product[fore]:
                    if str_list == [u'ε'] or if_prodiction(str_list,product_set):
                        product_set.append(fore)
                        m_changed = True

    #去除所有非产生符号的产生式
    for fore in CFG_product:
        if fore not in product_set:
            CFG['final_Production'].pop(fore)
        for str_list in CFG_product[fore]:
            if_pro = True
            for i in str_list:
                if i not in product_set:
                    if_pro = False
            if if_pro == False:
                CFG['final_Production'][fore].remove(str_list)
    #去除所有非产生的符号
    for ter in CFG['Terminal']:
        if ter not in product_set:
            CFG['Terminal'].remove(ter)
    for var in CFG['Variable']:
        if var not in product_set:
            CFG['Variable'].remove(var)
    return CFG

#判断一条产生式是否是可产生的
def if_prodiction(str_list,product_set):
    for i in str_list:
        if i not in product_set:
            return False
    return True

#去除非可达式
def remove_not_reachable(CFG):
    #if_null_flag记录每一条产生式是否可空
    CFG_product = copy.deepcopy(CFG['final_Production'])
    reachable_set = []
    #S可达
    reachable_set.append(CFG['Start'])
    #找出所有可达符号
    m_changed = True
    while m_changed:
        m_changed = False
        for fore in CFG_product:
            if fore in reachable_set:
                for str_list in CFG_product[fore]:
                    for m_char in str_list:
                        if m_char not in reachable_set:
                            reachable_set.append(m_char)
                            m_changed = True

    #去除所有非产生符号的产生式
    for fore in CFG_product:
        if fore not in reachable_set:
            CFG['final_Production'].pop(fore)
            continue
        for str_list in CFG_product[fore]:
            if_pro = True
            for i in str_list:
                if i not in reachable_set:
                    if_pro = False
            if if_pro == False:
                 CFG['final_Production'][fore].remove(str_list)
    #去除所有非产生的符号
    for ter in CFG['Terminal']:
        if ter not in reachable_set:
            CFG['Terminal'].remove(ter)
    for var in CFG['Variable']:
        if var not in reachable_set:
            CFG['Variable'].remove(var)
    return CFG

def turn_CNF(CFG):
    #为所有非唯一产生终结符的终结符增加变量
    ter_var_dict = {}
    #寻找唯一产生的字符串
    CFG_product = copy.deepcopy(CFG['final_Production'])
    for fore in CFG_product:
        if len(CFG_product[fore]) == 1 and CFG_product[fore][0] in CFG['Terminal'] and CFG_product[fore][0] not in ter_var_dict:
            ter_var_dict[CFG_product[fore][0]] = fore
    #为所有终结符配一个变元
    m_index = 0
    for ter in CFG['Terminal']:
        if ter not in ter_var_dict:
            while ('Q'+str(m_index)) in CFG['Variable']\
                or ('Q'+str(m_index)) in CFG['Terminal']:
                m_index += 1
            ter_var_dict[ter] =('Q'+str(m_index))
            CFG['Variable'].append('Q'+str(m_index))
    #将产生式中的终结符替换
    for fore in CFG_product:
        for s in range(len(CFG_product[fore])):
            str_list =  CFG_product[fore][s]
            if len(str_list) > 1:
                for i in range(len(str_list)):
                    if str_list[i] in CFG['Terminal']:
                        CFG['final_Production'][fore][s][i] = ter_var_dict[str_list[i]]


    #级联拆解
    new_fore_char = {}
    m_changed = True
    while m_changed:
        m_changed = False
        #拷贝一份产生式
        CFG_product = copy.deepcopy(CFG['final_Production'])
        for fore in CFG_product:
            for s in range(len(CFG_product[fore])):
                str_list =  CFG_product[fore][s]
                if len(str_list) > 2:
                    second = str_list[1:len(str_list)]
                    #second.sort()
                    state = '_'.join(second)
                    if state in new_fore_char:
                        CFG['final_Production'][fore][s] = [str_list[0],new_fore_char[state]]
                    else:
                        #创建新的变元
                        #变元名字
                        #m_index = 0
                        while ('Q'+str(m_index)) in CFG['Variable']\
                            or ('Q'+str(m_index)) in CFG['Terminal']:
                            m_index += 1
                        new_var = 'Q'+str(m_index)
                        #加入新的变元
                        CFG['Variable'].append(new_var)
                        new_fore_char[state] = new_var
                        #修改，增加产生式
                        CFG['final_Production'][fore][s] = [str_list[0],new_var]
                        CFG['final_Production'][new_var] = copy.deepcopy(second)
                    m_changed = True
    return CFG

#CFG化简函数
def CFGsimplify(CFG):
    #从前端得到FA和judgeString的值
    CFG_product = CFG['final_Production']
    #建立产生式flag
    CFG = removeNull(CFG)
    CFG = remove_unit_prod(CFG)
    #CFG = remove_notproduct(CFG)
    #CFG = remove_not_reachable(CFG)
    CFG = turn_CNF(CFG)
    return CFG


def fore_CFGsimplify(request):
    global CFG
    #CFG = simplejson.loads(request.raw_post_data)
    CFG = parse_finalP(CFG)
    CFG = CFGsimplify(CFG)
    CFG = connnect_preP(CFG)
    json=simplejson.dumps(CFG)
    return HttpResponse(json)


