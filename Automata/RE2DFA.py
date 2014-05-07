#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
import datetime
from django.shortcuts import render_to_response
from django.utils import simplejson
import copy
#test样例，json格式

REstring = '((e+g)*+ee)*g'
REstring = '(1+01)*0*'
T_stack = []  #表达式栈，存储字符串等
connect = 0   #状态位，记录是否出现两位连续的字符串。
OP_stack = ['#'] #运算符栈，预存入‘#’
leaf_node = {'0':[]} #存放叶子节点的followpos
leaf_count = 1 #叶子节点数量
g_input = []

def CrtLeafNode(ch):
    global T_stack,leaf_node,leaf_count,g_input
    new_node = {
        'type':'leaf',
        'data':'',
        'left_child':{},
        'right_child':{},
        'nullable':False,
        'firstpos':[leaf_count],
        'lastpos':[leaf_count],
        'number':leaf_count,
    }
    new_node['data'] = ch
    if ch == u'ε':
        new_node['nullable'] = True
        new_node['firstpos'] = ['#']
        new_node['lastpos'] = ['#']
    leaf_node[str(leaf_count)]={'data':ch,'followpos':[],}
    T_stack.append(new_node)
    leaf_count += 1
    if ch != '#' and ch != u'ε' and ch not in g_input:
        g_input.append(ch)
    return True

def CrtSubTree(ch):
    global T_stack,OP_stack,leaf_node
    new_tree = {
        'type':'subtree',
        'data':ch,
        'left_child':{},
        'right_child':{},
        'nullable':True,
        'firstpos':[leaf_count],
        'lastpos':[leaf_count],
    }
    #不同类型
    if ch == '*':
        if len(T_stack) < 1:
            return False
        if T_stack[-1]['data'] == '*':
            return True
        new_tree['left_child'] = T_stack.pop()
        #null，first，last，
        new_tree['nullable'] = True
        new_tree['firstpos'] = copy.deepcopy(new_tree['left_child']['firstpos'])
        new_tree['lastpos'] = copy.deepcopy(new_tree['left_child']['lastpos'])
        #follow修改
        for pos in new_tree['lastpos']:
            if pos != '#':
            #leaf_node[pos]['followpos'].extend(new_tree['firstpos'])
                leaf_node[str(pos)]['followpos'] = list(set(leaf_node[str(pos)]['followpos']) | set(new_tree['firstpos']))
                if '#' in leaf_node[str(pos)]['followpos'] and len(leaf_node[str(pos)]['followpos']) > 1:
                    leaf_node[str(pos)]['followpos'].remove('#')
    else:#二元操作符
        if len(T_stack) < 2:
            return False
        temp2 = T_stack.pop()
        new_tree['right_child'] = temp2
        temp1  = T_stack.pop()
        new_tree['left_child'] = temp1
        if ch == '$':
            #null，first，last，
            new_tree['nullable'] = temp1['nullable'] and temp2['nullable']
            new_tree['firstpos'] = copy.deepcopy(temp1['firstpos'])
            if temp1['nullable']:
                #new_tree['firstpos'].extend(temp2['firstpos'])
                new_tree['firstpos'] = list(set(new_tree['firstpos']) | set(temp2['lastpos']))
                if '#' in new_tree['firstpos'] and len(new_tree['firstpos']) > 1:
                    new_tree['firstpos'].remove('#')
            new_tree['lastpos'] = copy.deepcopy(temp2['lastpos'])
            if temp2['nullable']:
                #new_tree['lastpos'].extend(temp1['lastpos'])
                 new_tree['lastpos'] = list(set(new_tree['lastpos']) | set(temp1['lastpos']))
                 if '#' in new_tree['lastpos'] and len(new_tree['lastpos']) > 1:
                    new_tree['lastpos'].remove('#')
            #follow修改
            for pos in temp1['lastpos']:
                #leaf_node[pos]['followpos'] = copy.deepcopy(temp2['firstpos'])
                #leaf_node[pos]['followpos'].extend(temp2['firstpos'])
                if pos != '#':
                    leaf_node[str(pos)]['followpos'] = list(set(leaf_node[str(pos)]['followpos']) | set(temp2['firstpos']))
                    if '#' in leaf_node[str(pos)]['followpos'] and len(leaf_node[str(pos)]['followpos']) > 1:
                        leaf_node[str(pos)]['followpos'].remove('#')
        elif ch == '+':
            #null，first，last，
            new_tree['nullable'] = temp1['nullable'] or temp2['nullable']
            #new_tree['firstpos'] = temp1['firstpos'] + temp2['firstpos']
            new_tree['firstpos'] = list(set(temp1['firstpos']) | set(temp2['firstpos']))
            if '#' in new_tree['firstpos'] and len(new_tree['firstpos']) > 1:
                new_tree['firstpos'].remove('#')
            #new_tree['lastpos'] = temp1['lastpos'] + temp2['lastpos']
            new_tree['lastpos'] = list(set(temp1['lastpos']) | set(temp2['lastpos']))
            if '#' in new_tree['lastpos'] and len(new_tree['lastpos']) > 1:
                new_tree['lastpos'].remove('#')

    T_stack.append(new_tree)
    return True

def CrtRETree(REstring):
    global T_stack,OP_stack
    OP_Char = ['$','+','*','(',')','#']
    op_index = {'#':0,'(':1,'+':2,'$':3,'*':4}
    index = 0   #当前进行到的字符次序
    #connect = 0 #connnect = 0:没有压入char；=1：已经压入了一个，不能合并，=2：已经压入了两个，合并之前的两个，留下这个不能合并
    root = {} #根节点
    ch = REstring[index]
    while(ch != '#' or OP_stack != []):
        if (ch not in OP_Char):
            if CrtLeafNode(ch) == False:
                return False,[]
        else:
            if ch == '(':
                OP_stack.append(ch)
            elif ch == ')':
                ch = OP_stack.pop()
                if ch == '#':
                    return False,[]
                while ch != '(':
                    if CrtSubTree(ch) == False:
                        return False,[]
                    ch = OP_stack.pop()
                    if ch == '#':
                        return False,[]
            elif ch == '*':
                if CrtSubTree(ch) == False:
                    return False,[]
            else:   #  +运算和$运算
                #栈顶与当前运算符比较, 高则进栈，低则出栈并建子树
                while op_index[ch] <= op_index[OP_stack[-1]] and OP_stack[-1] != '#':
                   if CrtSubTree(OP_stack.pop()) == False:
                       return  False,[]
                if ch!= '#':
                    OP_stack.append(ch)
        if ch != '#':
            index += 1
            ch = REstring[index]
        else:
            if CrtLeafNode(OP_stack.pop()) == False:
                return False,[]
            if CrtSubTree('$') == False:
                return False,[]
            root = T_stack.pop()
    return True,root

def checkREstring(REstring):
    REstring = list(REstring)
    OP_Char = ['$','+','*','(',')','#']
    left_bracket = 0
    ifChange = True
    #字符串错误检验
    for i in range(0,len(REstring)):
        if REstring[i] == '#' or REstring[i] == '$':
            return False,''
        if REstring[i] == '+':
            if i == 0 or i == len(REstring) - 1 \
                or (i > 0 and REstring[i-1] in OP_Char and REstring[i-1] != ')' and REstring[i-1] != '*')\
                or (i < len(REstring) - 1 and REstring[i+1] in OP_Char and REstring[i+1] != '('):
                return False,[]
        if REstring[i] == '*':
            if i == 0  \
                or (REstring[i-1] in OP_Char and REstring[i-1] != ')'):
                return False,[]
        if REstring[i] == '(':
            left_bracket += 1
        if REstring[i] == ')':
            left_bracket -= 1
            if left_bracket < 0:
                return False,[]

    if left_bracket > 0:
        return  False,[]

    while ifChange:
        ifChange = False
        for i in range(len(REstring)):
            if i < len(REstring)-1 and (REstring[i] not in OP_Char) and (REstring[i+1] not in OP_Char):
                REstring.insert(i+1,'$')
                ifChange = True
            if (REstring[i] not in OP_Char) and ((REstring[i-1] == ')' or REstring[i-1] == '*')):
                REstring.insert(i,'$')
                ifChange = True

    return True,''.join(REstring) + '#'


def fore_RE2DFA(request):
    global T_stack,OP_stack,REstring,g_input
    #REstring = simplejson.loads(request.raw_post_data)
    DFA = RE2DFA(REstring)
    json=simplejson.dumps(DFA)
    return HttpResponse(json)

#RE中不能出现#！！！！！！！！！！！
#RE转DFA函数
def RE2DFA(REstring):
    global T_stack,OP_stack,g_input
    #RE来自于前端的信息转化
    #REstring = simplejson.loads(request.raw_post_data)
    ifTure,REstring = checkREstring(REstring)
    if not ifTure:
        return HttpResponse([])
    ifSuc,root = CrtRETree(REstring)
    if not ifSuc:
        return HttpResponse([])
    #构建DFA
    DFA = {
        'type':'DFA',
        'state':{
        },
        'input':[],
        'start':'Q0',
        'final':[],
    }
    DFA['input'] = g_input
    #去掉null
    if u'ε' in DFA['input']:
        DFA['input'].remove(u'ε')

    add_state = {}
    root['firstpos'].sort()
    for i in range(0,len(root['firstpos'])):
        root['firstpos'][i] = str(root['firstpos'][i])
    temp = '_'.join(root['firstpos'])
    add_state[temp] = [0,False,root['firstpos']]
    DFA['state']['Q0'] = {
        'name':temp,
        'is_start':True,
        'is_final':False,
        'transition':{
        }
    }
    if str(leaf_count-1) in root['firstpos']:
        DFA['final'].append('Q0')
        DFA['state']['Q0']['is_final'] = True
    state_num = 1
    mark_num = 0
    while mark_num < len(add_state):
        for state in add_state:
            if add_state[state][1] == False:
                add_state[state][1] = True
                mark_num += 1
                for m_input in g_input:
                    U_follow = []
                    for pos in add_state[state][2]:
                        if leaf_node[str(pos)]['data'] == m_input:
                            U_follow =  list(set(U_follow) | set(leaf_node[str(pos)]['followpos']))
                    U_follow.sort()
                    for i in range(0,len(U_follow)):
                        U_follow[i] = str(U_follow[i])
                    temp = '_'.join(U_follow)
                    #如果不在add_state里面，则添加，并添加入DFA的state，未标记
                    if temp not in add_state:
                        add_state[temp] = [state_num,False,U_follow]
                        DFA['state']['Q'+str(state_num)] = {
                            'name':temp,
                            'is_start':False,
                            'is_final':False,
                            'transition':{
                            }
                        }
                        #如果包含最后一个节点leaf_count-1，则是终结状态
                        if str(leaf_count-1) in U_follow:
                            DFA['final'].append('Q'+str(state_num))
                            DFA['state']['Q'+str(state_num)]['is_final'] = True
                        state_num += 1
                    #添加转移
                    DFA['state']['Q'+str(add_state[state][0])]['transition'][m_input] = 'Q'+str(add_state[temp][0])
                break
    return DFA

