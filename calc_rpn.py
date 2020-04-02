import operator
import sys
import ply.lex as lex
import ply.yacc as yacc

keywords = (
    'IF', 'WHILE', 'FOR', 'ELSE', 'PRINT', 'FUNCTION'
)

tokens = (
             'NAME', 'NUMBER', 'OPERATOR', 'COMPARATOR'
         ) + keywords

literals = ['=', '+', '-', '*', '/', '(', ')', '^', '<', '>', '!', ';', '{', '}', ',', '%']
operators = {'+': operator.add, '-': operator.sub, '*': operator.mul, '/': operator.truediv, '^': operator.pow,
             '%': operator.mod}
comparators = {'<=': operator.le, '>=': operator.ge, '<': operator.lt, '>': operator.gt, '==': operator.eq,
               '!=': operator.ne,
               }
names = {}
functions = {}


def is_integer(value):
    if value % 1 == 0:
        return True
    return False


def t_NUMBER(t):
    r'\d*\.\d+|\d+\.?'
    t.value = float(t.value)
    if is_integer(t.value):
        t.value = int(t.value)
    return t


def t_NAME(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    if t.value.upper() in keywords:
        t.type = t.value.upper()
    return t


def t_OPERATOR(t):
    r'\+|-|\*|/|\^|\%'
    t.value = operators[t.value]
    return t


def t_COMPARATOR(t):
    r'<|>|<=|>=|!=|=='
    t.value = comparators[t.value]
    return t


t_ignore = ' \t'


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


lexer = lex.lex()


def p_program_one(p):
    '''program : instructions instructions'''
    p[0] = ('program', p[1]) + p[2][1:]


def p_program(p):
    '''program : instructions'''
    p[0] = ('program', p[1])


def p_function(p):
    '''function : FUNCTION NAME params  block'''
    p[0] = ('function', p[2], p[3], p[4])


def p_params_one(p):
    '''params : '(' name ')' '''
    p[0] = (p[2],)


def p_params(p):
    '''params : '(' more_names ')' '''
    p[0] = p[2]


def p_params_void(p):
    '''params : '(' ')' '''
    p[0] = ()


def p_more_names(p):
    '''more_names : name ',' name'''
    p[0] = (p[1], p[3])


def p_more_names_more(p):
    '''more_names : name ',' more_names '''
    p[0] = p[3] + (p[1],)


def p_call_statement(p):
    '''statement : call_function'''
    p[0] = p[1]


def p_parameters_one(p):
    '''parameters : '(' statement ')' '''
    p[0] = (p[2],)


def p_parameters(p):
    '''parameters : '(' more_statements ')' '''
    p[0] = p[2]


def p_parameters_void(p):
    '''parameters : '(' ')' '''
    p[0] = ()


def p_more_statements_more(p):
    '''more_statements :  statement ',' more_statements'''
    p[0] = p[3] + (p[1],)


def p_more_statements(p):
    '''more_statements : statement ',' statement '''
    p[0] = (p[1], p[3])


def p_call_function(p):
    '''call_function : NAME parameters '''
    p[0] = ('call_function', p[1], p[2])


def p_for(p):
    '''for : FOR '(' assigment ';' relation ';' statement ')' block'''
    p[0] = ('for', p[3], p[5], p[7], p[9])


def p_if_else(p):
    '''if : IF '(' relation ')' block ELSE block'''
    p[0] = ('if', p[3], p[5], p[7])


def p_while(p):
    '''while : WHILE '(' relation ')' block'''
    p[0] = ('while', p[3], p[5])


def p_print_statement(p):
    '''statement : print'''
    p[0] = p[1]


def p_print(p):
    '''print : PRINT '(' statement ')' '''
    p[0] = ('print', p[3])


def p_if(p):
    '''if : IF '(' relation ')' block'''
    p[0] = ('if', p[3], p[5], None)


def p_statement_assign(p):
    '''statement : assigment'''
    p[0] = p[1]


def p_assign(p):
    """assigment : name '=' expression"""
    p[0] = ("assign", p[1][1], p[3])


def p_relation(p):
    '''relation : statement COMPARATOR statement'''
    p[0] = ('relation', p[2], p[1], p[3])


def p_block(p):
    '''block : '{' instructions '}' '''
    p[0] = ('block', p[2])


def p_instructions(p):
    '''instructions : statement ';' instructions
                    | statement ';' '''
    if len(p) == 3:
        p[0] = ('instructions', p[1])
    else:
        p[0] = ('instructions', p[1]) + p[3][1:]


def p_if_instructions_instructions(p):
    '''instructions : if instructions
                    | for instructions
                    | while instructions
                    | function instructions'''
    p[0] = ('instructions', p[1]) + p[2][1:]


def p_instructions_if(p):
    '''instructions : if
                    | for
                    | while
                    | function'''
    p[0] = ('instructions', p[1])


def p_statement_expr(p):
    'statement : expression'
    p[0] = ('expression', p[1])


def p_name(p):
    'name : NAME'
    p[0] = ('name', p[1])


def calculate_tuple(tuple_epx):
    if type(tuple_epx) != tuple:
        return tuple_epx
    if tuple_epx[0] == 'name':
        return get_name(tuple_epx[1])
    return tuple_epx[0](calculate_tuple(tuple_epx[1]), calculate_tuple(tuple_epx[2]))


def get_name(key):
    return names[key]


def p_subexpr(p):
    "subexpression : variable expression OPERATOR"
    p[0] = (p[3], p[1], p[2])


def p_subexpr_right(p):
    "subexpression : subexpression expression OPERATOR"
    p[0] = (p[3], p[1], p[2])


def p_subexpr_double(p):
    "subexpression : subexpression subexpression OPERATOR"
    p[0] = (p[3], p[1], p[2])


def p_expression_sub(p):
    '''expression : subexpression'''
    p[0] = p[1]


def p_expression_number(p):
    "expression : variable"
    p[0] = p[1]


def p_name_connect_number(p):
    '''variable : NUMBER
                | name'''
    p[0] = p[1]


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


def evaluate_relation(relation):
    return relation[1](execute(relation[2]), execute(relation[3]))


def for_operation(assigment, relation, statement, block):
    execute(assigment)
    while evaluate_relation(relation):
        execute(block)
        execute(statement)


def while_operation(relation, block):
    while evaluate_relation(relation):
        execute(block)


def function_operation(function_name, params, block):
    functions[function_name] = (block, params)


def call_function_operation(function_name, parameters):
    function = functions[function_name]
    params = function[1]
    for i in range(len(parameters)):
        names[params[i][1]] = execute(parameters[i])
    execute(function[0])


def program_operation(tree):
    for instructions in tree[1][1:]:
        execute(instructions)



def execute(tree):
    try:
        if tree is None:
            return
        elif type(tree) is int or type(tree) is float:
            return tree
        elif tree[0] == 'for':
            for_operation(tree[1], tree[2], tree[3], tree[4])
        elif tree[0] == 'program':
            program_operation(tree)
        elif tree[0] == 'expression':
            return calculate_tuple(tree[1])
        elif tree[0] == 'name':
            return names[tree[1]]
        elif tree[0] == 'print':
            print(execute(tree[1]))
        elif tree[0] == 'function':
            function_operation(tree[1], tree[2], tree[3])
        elif tree[0] == 'call_function':
            call_function_operation(tree[1], tree[2])
        elif tree[0] == 'instructions':
            for instruction in tree[1:]:
                execute(instruction)
        elif tree[0] == 'block':
            execute(tree[1])
        elif tree[0] == 'while':
            while_operation(tree[1], tree[2])
        elif tree[0] == 'assign':
            names[tree[1]] = execute(('expression', tree[2]))
        elif tree[0] == 'if':
            relation = tree[1]
            if evaluate_relation(relation):
                execute(tree[2])
            else:
                if tree[3] is not None:
                    execute(tree[3])
    except LookupError:
        print(f"Undefined name of function or variable")
        return


def parse(string):
    result = yacc.parse(string)
    # print('Tree: ', result)
    # print(functions)
    # print(names)
    execute(result)


parser = yacc.yacc()

if __name__ == '__main__':
    if len(sys.argv) == 2:
        try:
            file = open('example.txt').read()
            parse(file)
        except FileNotFoundError:
            print(f"Unable to open file '{sys.argv[1]}'")
    while True:
        try:
            s = input('calc > ')
        except EOFError:
            break
        if not s:
            continue
        parse(s)
