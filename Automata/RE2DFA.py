#encoding: utf-8
__author__ = 'manman'
#from django.template import Context
from django.http import HttpResponse
import datetime
from django.shortcuts import render_to_response
from django.utils import simplejson
import copy
#test样例，json格式

REstring = '(a+b)*abb'

T_stack = []  #表达式栈，存储字符串等
connect = 0   #状态位，记录是否出现两位连续的字符串。
OP_stack = ['#'] #运算符栈，预存入‘#’
leaf_node = [[]] #存放叶子节点的followpos
leaf_count = 1 #叶子节点数量


def CrtLeafNode(ch):
    global T_stack,leaf_node,leaf_count
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
    leaf_node.append({'data':ch,'followpos':[],})
    T_stack.append(new_node)
    leaf_count += 1
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
        if T_stack[0]['data'] == '*':
            return True
        new_tree['left_child'] = T_stack.pop()
        #null，first，last，
        new_tree['nullable'] = True
        new_tree['firstpos'] = copy.deepcopy(new_tree['left_child']['firstpos'])
        new_tree['lastpos'] = copy.deepcopy(new_tree['left_child']['lastpos'])
        #follow修改
        for pos in new_tree['lastpos']:
            leaf_node[pos]['followpos'] = copy.deepcopy(new_tree['firstpos'])
    else:#二元操作符
        if len(T_stack) < 2:
            return False
        temp2 = T_stack.pop()
        new_tree['right_child'] = temp2
        temp1  = T_stack.pop()
        new_tree['left_child'] = temp1
        if ch == '.':
            #null，first，last，
            new_tree['nullable'] = temp1['nullable'] and temp2['nullable']
            new_tree['firstpos'] = copy.deepcopy(temp1['firstpos'])
            if temp1['nullable']:
                new_tree['firstpos'].extend(temp2['firstpos'])
            new_tree['lastpos'] = copy.deepcopy(temp2['lastpos'])
            if temp1['nullable']:
                new_tree['lastpos'].extend(temp1['lastpos'])
            #follow修改
            for pos in temp1['lastpos']:
                leaf_node[pos]['followpos'] = copy.deepcopy(temp2['firstpos'])
        elif ch == '+':
            #null，first，last，
            new_tree['nullable'] = temp1['nullable'] or temp2['nullable']
            new_tree['firstpos'] = temp1['firstpos'] + temp2['firstpos']
            new_tree['lastpos'] = temp1['lastpos'] + temp2['lastpos']

    T_stack.append(new_tree)
    return True

def CrtRETree(REstring):
    global T_stack,OP_stack

    index = 0   #当前进行到的字符次序
    connect = 0 #connnect = 0:没有压入char；=1：已经压入了一个，不能合并，=2：已经压入了两个，合并之前的两个，留下这个不能合并
    root = {} #根节点
    ch = REstring[index]
    while(ch != '#' or OP_stack != []):
        if (ch not in ['+','*','(',')','#']):
            if connect < 2:
                if CrtLeafNode('ch') == False:
                    return False,[]
                connect += 1
            elif connect == 2:
                #合并前两个
                if CrtSubTree('.') == False:
                    return False,[]
                #压入现在的
                if CrtLeafNode(ch) == False:
                    return False,[]
        else:
            if ch == '(' or ch == '+':
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
                connect = 1
            elif ch == '*':
                if CrtSubTree(ch) == False:
                    return False,[]
                connect = 1
            elif ch == '#':
                ch = OP_stack.pop()
                if ch == '(':
                    return False,[]
                while ch != '#':
                    if CrtSubTree(ch) == False or len(OP_stack) == 0:
                        return False,[]
                    ch = OP_stack.pop()
                    if ch == '(':
                        return False,[]
                #最后，#，压入最后的"#"，链接
                if CrtLeafNode('#') == False:
                        return False,[]
                if CrtSubTree('.') == False:
                        return False,[]
                root = T_stack.pop()
                ch = '#'
                OP_stack = []
        if ch != '#':
            index += 1
            ch = REstring[index]
    return True,root

#RE中不能出现#！！！！！！！！！！！
#RE转DFA函数
def RE2DFA(request):
    global T_stack,OP_stack,REstring
    #RE来自于前端的信息转化
    #REstring = simplejson.loads(request.raw_post_data)
    REstring += '#'
    ifSuc,root = CrtRETree(REstring)

    json=simplejson.dumps(root)
    return HttpResponse(json)

