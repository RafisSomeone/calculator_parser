import sys
import math
import ply.yacc as yacc
import ply.lex as lex

sys.path.insert(0, "../..")

tokens = (
    'NAME', 'NUMBER', 'FUNCTION', 'EQUAL', 'DIFFERENT'
)

literals = ['=', '+', '-', '*', '/', '(', ')', '^', '<', '>', '!', ';']

# Tokens

t_NAME = r'[a-zA-Z_][a-zA-Z0-9_]*'
1

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


def t_EQUAL(t):
    r'\=\='
    t.value = '='
    return t


def t_DIFFERENT(t):
    r'\!\='
    t.value = '!'
    return t


def t_FUNCTION(t):
    r"sin|cos|tan|ln|sqrt|abs|exp"
    if t.value == "abs":
        function = math.fabs
    elif t.value == "ln":
        function = math.log
    else:
        function = getattr(math, t.value)
    t.value = (t.value, function)
    return t


t_ignore = " \t"


def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)


# Build the lexer

lexer = lex.lex()

# Parsing rules

precedence = (
    ('right', 'EQUAL'),
    ('right', 'DIFFERENT'),
    ('left', '+', '-'),
    ('left', '*', '/'),
    ('right', 'UMINUS'),
    ('right', 'FUNCTION'),
)

# dictionary of names
names = {}


def p_instructions(p):
    '''instructions : statement ';'
                    | statement
                    | statement ';' instructions'''
    pass


def p_expression_function(p):
    """expression : FUNCTION expression"""
    p[0] = p[1][1](p[2])


def p_statement_assign(p):
    'statement : NAME "=" expression'
    names[p[1]] = p[3]


def p_statement_expr(p):
    'statement : expression'
    print(p[1])


def p_expression_binop(p):
    '''expression : expression '+' expression
                  | expression '-' expression
                  | expression '*' expression
                  | expression '/' expression
                  | expression '^' expression
                  | expression '>' expression
                  | expression '<' expression
                  | expression EQUAL expression
                  | expression DIFFERENT expression'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        p[0] = p[1] / p[3]
    elif p[2] == '^':
        p[0] = p[1] ** p[3]
    elif p[2] == '<':
        p[0] = p[1] < p[3]
    elif p[2] == '>':
        p[0] = p[1] > p[3]
    elif p[2] == '=':
        p[0] = p[1] == p[3]
    elif p[2] == '!':
        p[0] = p[1] != p[3]


def p_expression_uminus(p):
    "expression : '-' expression %prec UMINUS"
    p[0] = -p[2]


def p_expression_group(p):
    "expression : '(' expression ')'"
    p[0] = p[2]


def p_expression_number(p):
    "expression : NUMBER"
    p[0] = p[1]


def p_expression_name(p):
    "expression : NAME"
    try:
        p[0] = names[p[1]]
    except LookupError:
        print("Undefined name '%s'" % p[1])
        p[0] = 0


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()

while True:
    try:
        s = input('calc > ')
    except EOFError:
        break
    if not s:
        continue
    yacc.parse(s)
