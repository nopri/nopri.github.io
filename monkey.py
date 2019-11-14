
#
# Simple implementation of The Monkey Programming Language
# interpreter in Python
# Monkey.py
# (c) Noprianto <nopri.anto@icloud.com>, 2019
# Website: nopri.github.io
# License: MIT
# Version: 0.9
#
# Compatible with Python 2 and Python 3
# Minimum Python version: 2.3
#
# Based on code (in Go programming language) in book:
# WRITING AN INTERPRETER IN GO
#
# For Monkey Programming Language interpreter in Java, please
# download Monkey.java or Monkey.jar (minimum Java version: 5.0). 
#
# How to use monkey.py:
# - Standalone
#   - No command line argument: interactive
#       python monkey.py
#       Monkey.py 0.9
#       Press ENTER to quit
#       >> let hello = "Hello World"
#       >> hello
#       "Hello World"
#       >> 
#   - Command line argument: try to interpret as file
#       python monkey.py test.monkey
#     If exception occurred: interpret the argument as monkey code 
#       python monkey.py "puts(1,2,3)"
#       1
#       2
#       3
#       null
# - Library
#   Please see the example below
#
# In monkey.py, it is possible to set initial environment
# when the interpreter is started. This allows integration
# with external applications. For example:
# code:
#
#    try:
#        from StringIO import StringIO
#    except:
#        from io import StringIO
#
#    from monkey import *
#
#    d = {'hello': 'Hello, World', 'test': True}
#    e = MonkeyEnvironment.from_dictionary(d)
#    o = StringIO() 
#    Monkey.evaluator_string('puts(hello); puts(test); ERROR;', e, output=o)
#    r = o.getvalue()
#    print(r)
#
# output:
#
#    Hello, World
#    true
#    ERROR: identifier not found: ERROR
#
#

import sys
import os

MONKEYPY_VERSION = '0.9'
MONKEYPY_TITLE = 'Monkey.py %s' %(MONKEYPY_VERSION)
MONKEYPY_MESSAGE = 'Press ENTER to quit'
MONKEYPY_LINESEP = os.linesep

class MonkeyToken:
    ILLEGAL = 'ILLEGAL'
    EOF = 'EOF'
    IDENT = 'IDENT'
    INT = 'INT'
    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    BANG = '!'
    ASTERISK = '*'
    SLASH = '/'
    LT = '<'
    GT = '>'
    COMMA = ','
    SEMICOLON = ';'
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    FUNCTION = 'FUNCTION'
    LET = 'LET'
    TRUE = 'true'
    FALSE = 'false'
    IF = 'if'
    ELSE = 'else'
    RETURN = 'return'
    EQ = '=='
    NOT_EQ = '!='
    STRING = 'STRING'
    LBRACKET = '['
    RBRACKET = ']'
    COLON = ':'

    def __init__(self, type_='', literal=''):
        self.type = type_
        self.literal = literal


class MonkeyLexer:
    KEYWORDS = {
                'fn': MonkeyToken.FUNCTION,
                'let': MonkeyToken.LET,
                'true': MonkeyToken.TRUE,
                'false': MonkeyToken.FALSE,
                'if': MonkeyToken.IF,
                'else': MonkeyToken.ELSE,
                'return': MonkeyToken.RETURN,
            }

    VALID_IDENTS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
    VALID_NUMBERS = '0123456789'
    WHITESPACES = [' ', '\t', '\r', '\n']

    def __init__(self, input_='', position=0, read=0, ch=''):
        self.input = input_
        self.position = position
        self.read = read
        self.ch = ch

    def read_char(self):
        if self.read >= len(self.input):
            self.ch = ''
        else:
            self.ch = self.input[self.read]
        self.position = self.read
        self.read += 1

    def peek_char(self):
        if self.read >= len(self.input):
            return ''
        else:
            return self.input[self.read]

    def new_token(self, token, t, ch):
        token.type = t
        token.literal = ch
        return token

    def next_token(self):
        t = MonkeyToken()

        self.skip_whitespace()

        if self.ch == '=':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                t = self.new_token(t, MonkeyToken.EQ, ch + self.ch)
            else:
                t = self.new_token(t, MonkeyToken.ASSIGN, self.ch)
        elif self.ch == '+':
            t = self.new_token(t, MonkeyToken.PLUS, self.ch)
        elif self.ch == '-':
            t = self.new_token(t, MonkeyToken.MINUS, self.ch)
        elif self.ch == '!':
            if self.peek_char() == '=':
                ch = self.ch
                self.read_char()
                t = self.new_token(t, MonkeyToken.NOT_EQ, ch + self.ch)
            else:
                t = self.new_token(t, MonkeyToken.BANG, self.ch)
        elif self.ch == '/':
            t = self.new_token(t, MonkeyToken.SLASH, self.ch)
        elif self.ch == '*':
            t = self.new_token(t, MonkeyToken.ASTERISK, self.ch)
        elif self.ch == '<':
            t = self.new_token(t, MonkeyToken.LT, self.ch)
        elif self.ch == '>':
            t = self.new_token(t, MonkeyToken.GT, self.ch)
        elif self.ch == ';':
            t = self.new_token(t, MonkeyToken.SEMICOLON, self.ch)
        elif self.ch == '(':
            t = self.new_token(t, MonkeyToken.LPAREN, self.ch)
        elif self.ch == ')':
            t = self.new_token(t, MonkeyToken.RPAREN, self.ch)
        elif self.ch == ',':
            t = self.new_token(t, MonkeyToken.COMMA, self.ch)
        elif self.ch == '+':
            t = self.new_token(t, MonkeyToken.PLUS, self.ch)
        elif self.ch == '{':
            t = self.new_token(t, MonkeyToken.LBRACE, self.ch)
        elif self.ch == '}':
            t = self.new_token(t, MonkeyToken.RBRACE, self.ch)
        elif self.ch == '':
            t.literal = ''
            t.type = MonkeyToken.EOF
        elif self.ch == '"':
            t.literal = self.read_string()
            t.type = MonkeyToken.STRING
        elif self.ch == '[':
            t = self.new_token(t, MonkeyToken.LBRACKET, self.ch)
        elif self.ch == ']':
            t = self.new_token(t, MonkeyToken.RBRACKET, self.ch)
        elif self.ch == ':':
            t = self.new_token(t, MonkeyToken.COLON, self.ch)
        else:
            if self.is_letter(self.ch):
                t.literal = self.read_ident()
                t.type = self.lookup_ident(t.literal)
                return t
            elif self.is_digit(self.ch):
                t.literal = self.read_number()
                t.type = MonkeyToken.INT
                return t
            else:
                t = self.new_token(t, MonkeyToken.ILLEGAL, self.ch)
        self.read_char()
        return t

    def read_ident(self):
        pos = self.position
        while True:
            if not self.ch:
                break
            test = self.is_letter(self.ch)
            if not test:
                break
            self.read_char()
        ret = self.input[pos:self.position]
        return ret

    def read_number(self):
        pos = self.position
        while True:
            if not self.ch:
                break
            test = self.is_digit(self.ch)
            if not test:
                break
            self.read_char()
        ret = self.input[pos:self.position]
        return ret

    def read_string(self):
        pos = self.position + 1
        while True:
            self.read_char()
            if self.ch == '"' or self.ch == '':
                break
        #
        ret = self.input[pos:self.position]
        return ret

    def lookup_ident(self, s):
        ret = MonkeyLexer.KEYWORDS.get(s)
        if ret:
            return ret
        return MonkeyToken.IDENT

    def is_letter(self, ch):
        return ch in MonkeyLexer.VALID_IDENTS

    def is_digit(self, ch):
        return ch in MonkeyLexer.VALID_NUMBERS
        
    def skip_whitespace(self):
        while (self.ch in MonkeyLexer.WHITESPACES):
            self.read_char()

    def new(s):
        l = MonkeyLexer()
        l.input = s
        l.read_char()
        return l
    new = staticmethod(new)


class MonkeyNode:
    def __init__(self):
        pass

    def token_literal(self):
        return ''

    def string(self):
        return ''


class MonkeyStatement(MonkeyNode):
    def __init__(self):
        pass

    def statement_node(self):
        pass


class MonkeyExpression(MonkeyNode):
    def __init__(self):
        pass

    def expression_node(self):
        pass


class MonkeyIdentifier(MonkeyExpression):
    def __init__(self, value=''):
        self.token = MonkeyToken()
        self.value = value

    def token_literal(self):
        return self.token.literal
    
    def string(self):
        return self.value


class MonkeyLetStatement(MonkeyStatement):
    def __init__(self):
       self.token = MonkeyToken()
       self.name = MonkeyIdentifier()
       self.value = MonkeyExpression()

    def token_literal(self):
        return self.token.literal

    def string(self):
        ret = self.token_literal() + ' '
        ret += self.name.string()
        ret += ' = '
        #
        if self.value:
           ret += self.value.string()
        #
        ret += ';'
        return ret
        

class MonkeyReturnStatement(MonkeyStatement):
    def __init__(self):
       self.token = MonkeyToken()
       self.return_value = MonkeyExpression()

    def token_literal(self):
        return self.token.literal

    def string(self):
        ret = self.token_literal() + ' '
        if self.return_value:
            ret += self.return_value.string()
        #
        ret += ';'
        return ret


class MonkeyExpressionStatement(MonkeyStatement):
    def __init__(self):
       self.token = MonkeyToken()
       self.expression = MonkeyExpression()

    def token_literal(self):
        return self.token.literal

    def string(self):
        if self.expression:
            return self.expression.string()
        #
        return ''


class MonkeyBlockStatement(MonkeyStatement):
    def __init__(self):
       self.token = MonkeyToken()
       self.statements = []

    def is_empty(self):
        return len(self.statements) == 0

    def token_literal(self):
        return self.token.literal

    def string(self):
        ret = '%s{%s' %(MONKEYPY_LINESEP, MONKEYPY_LINESEP)
        #
        for s in self.statements:
            ret += '%s;%s' %(s.string(), MONKEYPY_LINESEP)
        #
        ret += '}%s' %(MONKEYPY_LINESEP)
        return ret


class MonkeyIntegerLiteral(MonkeyExpression):
    def __init__(self, value=None):
       self.token = MonkeyToken()
       self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token.literal


class MonkeyStringLiteral(MonkeyExpression):
    def __init__(self, value=''):
       self.token = MonkeyToken()
       self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token.literal


class MonkeyFunctionLiteral(MonkeyExpression):
    def __init__(self):
       self.token = MonkeyToken()
       self.parameters = []
       self.body = MonkeyBlockStatement()

    def token_literal(self):
        return self.token.literal

    def string(self):
        params = []
        for p in self.parameters:
            params.append(p.string())
        #
        ret = self.token_literal()
        ret += '('
        ret += ', '.join(params)
        ret += ')'
        ret += self.body.string()
        #
        return ret


class MonkeyCallExpression(MonkeyExpression):
    def __init__(self):
       self.token = MonkeyToken()
       self.function = MonkeyExpression()
       self.arguments = []

    def token_literal(self):
        return self.token.literal

    def string(self):
        args = []
        for a in self.arguments:
            args.append(a.string())
        #
        ret = self.function.string()
        ret += '('
        ret += ', '.join(args)
        ret += ')'
        #
        return ret


class MonkeyBoolean(MonkeyExpression):
    def __init__(self, value=None):
       self.token = MonkeyToken()
       self.value = value

    def token_literal(self):
        return self.token.literal

    def string(self):
        return self.token.literal


class MonkeyPrefixExpression(MonkeyExpression):
    def __init__(self):
       self.token = MonkeyToken()
       self.operator = ''
       self.right = MonkeyExpression()

    def token_literal(self):
        return self.token.literal

    def string(self):
        ret = '('
        ret += self.operator
        ret += self.right.string()
        ret += ')'
        #
        return ret


class MonkeyInfixExpression(MonkeyExpression):
    def __init__(self):
       self.token = MonkeyToken()
       self.left = MonkeyExpression()
       self.operator = ''
       self.right = MonkeyExpression()

    def token_literal(self):
        return self.token.literal

    def string(self):
        ret = '('
        ret += self.left.string()
        ret += ' ' + self.operator + ' '
        ret += self.right.string()
        ret += ')'
        #
        return ret


class MonkeyIfExpression(MonkeyExpression):
    def __init__(self):
       self.token = MonkeyToken()
       self.condition = MonkeyExpression()
       self.consequence = MonkeyBlockStatement()
       self.alternative = MonkeyBlockStatement()

    def token_literal(self):
        return self.token.literal

    def string(self):
        ret = 'if'
        ret += self.condition.string()
        ret += ' '
        ret += self.consequence.string()
        #
        if not self.alternative.is_empty():
            ret += ' else '
            ret += self.alternative.string()
        #
        return ret


class MonkeyArrayLiteral(MonkeyExpression):
    def __init__(self):
       self.token = MonkeyToken()
       self.elements = []

    def token_literal(self):
        return self.token.literal

    def string(self):
        elements = []
        for e in self.elements:
            elements.append(e.string())
        #
        ret = '['
        ret += ', '.join(elements)
        ret += ']'
        #
        return ret


class MonkeyIndexExpression(MonkeyExpression):
    def __init__(self):
       self.token = MonkeyToken()
       self.left = MonkeyExpression()
       self.index = MonkeyExpression()

    def token_literal(self):
        return self.token.literal

    def string(self):
        ret = '('
        ret += self.left.string()
        ret += '['
        ret += self.index.string()
        ret += '])'
        #
        return ret


class MonkeyHashLiteral(MonkeyExpression):
    def __init__(self):
       self.token = MonkeyToken()
       self.pairs = {}

    def token_literal(self):
        return self.token.literal

    def string(self):
        pairs = []
        for k in self.pairs.keys():
            v = self.pairs.get(k)
            pairs.append('%s:%s' %(k.string(), v.string()))
        #
        ret = '{'
        ret += ', '.join(pairs)
        ret += '}'
        #
        return ret


class MonkeyParser:
    LOWEST = 1
    EQUALS = 2
    LESSGREATER = 3
    SUM = 4
    PRODUCT = 5
    PREFIX = 6
    CALL = 7
    INDEX = 8

    PRECEDENCES = {
        MonkeyToken.LPAREN: CALL,
        MonkeyToken.EQ: EQUALS,
        MonkeyToken.NOT_EQ: EQUALS,
        MonkeyToken.LT: LESSGREATER,
        MonkeyToken.GT: LESSGREATER,
        MonkeyToken.PLUS: SUM,
        MonkeyToken.MINUS: SUM,
        MonkeyToken.SLASH: PRODUCT,
        MonkeyToken.ASTERISK: PRODUCT,
        MonkeyToken.LBRACKET: INDEX,
    }

    def __init__(self):
        self.lexer = None
        self.cur_token = None
        self.peek_token = None
        self.errors = []
        self.prefix_parse_fns = {}
        self.infix_parse_fns = {}
        #
        self.register_prefix(MonkeyToken.IDENT, self.parse_identifier)
        self.register_prefix(MonkeyToken.INT, self.parse_integer_literal)
        self.register_prefix(MonkeyToken.BANG, self.parse_prefix_expression)
        self.register_prefix(MonkeyToken.MINUS, self.parse_prefix_expression)
        self.register_prefix(MonkeyToken.TRUE, self.parse_boolean)
        self.register_prefix(MonkeyToken.FALSE, self.parse_boolean)
        self.register_prefix(MonkeyToken.LPAREN, self.parse_grouped_expression)
        self.register_prefix(MonkeyToken.IF, self.parse_if_expression)
        self.register_prefix(MonkeyToken.FUNCTION, self.parse_function_literal)
        self.register_prefix(MonkeyToken.STRING, self.parse_string_literal)
        self.register_prefix(MonkeyToken.LBRACKET, self.parse_array_literal)
        self.register_prefix(MonkeyToken.LBRACE, self.parse_hash_literal)
        #
        self.register_infix(MonkeyToken.PLUS, self.parse_infix_expression)
        self.register_infix(MonkeyToken.MINUS, self.parse_infix_expression)
        self.register_infix(MonkeyToken.SLASH, self.parse_infix_expression)
        self.register_infix(MonkeyToken.ASTERISK, self.parse_infix_expression)
        self.register_infix(MonkeyToken.EQ, self.parse_infix_expression)
        self.register_infix(MonkeyToken.NOT_EQ, self.parse_infix_expression)
        self.register_infix(MonkeyToken.LT, self.parse_infix_expression)
        self.register_infix(MonkeyToken.GT, self.parse_infix_expression)
        self.register_infix(MonkeyToken.LPAREN, self.parse_call_expression)
        self.register_infix(MonkeyToken.LBRACKET, self.parse_index_expression)

    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.next_token()

    def parse_program(self):
        program = MonkeyProgram()
        
        while self.cur_token.type != MonkeyToken.EOF:
            s = self.parse_statement()
            if s:
                program.statements.append(s)
            self.next_token()

        return program

    def parse_statement(self):
        if self.cur_token.type == MonkeyToken.LET:
            return self.parse_let_statement()
        elif self.cur_token.type == MonkeyToken.RETURN:
            return self.parse_return_statement()
        else:
            return self.parse_expression_statement()
        return None

    def parse_let_statement(self):
        s = MonkeyLetStatement()
        s.token = self.cur_token
        if not self.expect_peek(MonkeyToken.IDENT):
            return None
        #
        s.name = MonkeyIdentifier()
        s.name.token = self.cur_token
        s.name.value = self.cur_token.literal
        if not self.expect_peek(MonkeyToken.ASSIGN):
            return None
        #
        self.next_token()
        s.value = self.parse_expression(self.LOWEST)
        if self.peek_token_is(MonkeyToken.SEMICOLON):
            self.next_token()
        #
        return s

    def parse_return_statement(self):
        s = MonkeyReturnStatement()
        s.token = self.cur_token

        self.next_token()

        s.return_value = self.parse_expression(self.LOWEST)
        if self.peek_token_is(MonkeyToken.SEMICOLON):
            self.next_token()
        #
        return s

    def parse_expression_statement(self):
        s = MonkeyExpressionStatement()
        s.token = self.cur_token
        s.expression = self.parse_expression(self.LOWEST)
        #
        if self.peek_token_is(MonkeyToken.SEMICOLON):
            self.next_token()
        #
        return s

    def parse_block_statement(self):
        block = MonkeyBlockStatement()
        block.token = self.cur_token
        #
        self.next_token()
        while not self.cur_token_is(MonkeyToken.RBRACE) and \
            not self.cur_token_is(MonkeyToken.EOF):
            s = self.parse_statement()
            if s is not None:
                block.statements.append(s)
            self.next_token()
        #
        return block

    def parse_expression(self, precedence):
        prefix = self.prefix_parse_fns.get(self.cur_token.type)
        if prefix is None:
            self.no_prefix_parse_fn_error(self.cur_token.type)
            return None
        left_exp = prefix()
        #
        while not self.peek_token_is(MonkeyToken.SEMICOLON) and \
            precedence < self.peek_precedence():
            infix = self.infix_parse_fns.get(self.peek_token.type)
            if infix is None:
                return left_exp
            #
            self.next_token()
            left_exp = infix(left_exp)
        #
        return left_exp

    def parse_identifier(self):
        ret = MonkeyIdentifier()
        ret.token = self.cur_token
        ret.value = self.cur_token.literal
        return ret

    def parse_integer_literal(self):
        lit = MonkeyIntegerLiteral()
        lit.token = self.cur_token
        try:
            test = int(self.cur_token.literal)
        except:
            msg = 'could not parse %s as integer' %(self.cur_token.literal)
            self.errors.append(msg)
            return None
        #
        lit.value = int(self.cur_token.literal)
        return lit

    def parse_string_literal(self):
        lit = MonkeyStringLiteral()
        lit.token = self.cur_token
        lit.value = self.cur_token.literal
        return lit
    
    def parse_array_literal(self):
        array = MonkeyArrayLiteral()
        array.token = self.cur_token
        array.elements = self.parse_expression_list(MonkeyToken.RBRACKET)
        return array
    
    def parse_hash_literal(self):
        h = MonkeyHashLiteral()
        h.token = self.cur_token
        #
        while not self.peek_token_is(MonkeyToken.RBRACE):
            self.next_token()
            key = self.parse_expression(self.LOWEST)
            #
            if not self.expect_peek(MonkeyToken.COLON):
                return None
            #
            self.next_token()
            value = self.parse_expression(self.LOWEST)
            #
            h.pairs[key] = value
            #
            if not self.peek_token_is(MonkeyToken.RBRACE) and \
                not self.expect_peek(MonkeyToken.COMMA):
                return None
        #
        if not self.expect_peek(MonkeyToken.RBRACE):
            return None
        #
        return h
    
    def parse_boolean(self):
        ret = MonkeyBoolean()
        ret.token = self.cur_token
        ret.value = self.cur_token_is(MonkeyToken.TRUE)
        return ret
    
    def parse_prefix_expression(self):
        e = MonkeyPrefixExpression()
        e.token = self.cur_token
        e.operator = self.cur_token.literal
        #
        self.next_token()
        e.right = self.parse_expression(self.PREFIX)
        #
        return e

    def parse_infix_expression(self, left):
        e = MonkeyInfixExpression()
        e.token = self.cur_token
        e.operator = self.cur_token.literal
        e.left = left
        #
        precedence = self.cur_precedence()
        self.next_token()
        e.right = self.parse_expression(precedence)
        #
        return e

    def parse_grouped_expression(self):
        self.next_token()
        e = self.parse_expression(self.LOWEST)
        #
        if not self.expect_peek(MonkeyToken.RPAREN):
            return None
        #
        return e

    def parse_if_expression(self):
        e = MonkeyIfExpression()
        e.token = self.cur_token
        #
        if not self.expect_peek(MonkeyToken.LPAREN):
            return None
        #
        self.next_token()
        e.condition = self.parse_expression(self.LOWEST)
        #
        if not self.expect_peek(MonkeyToken.RPAREN):
            return None
        #
        if not self.expect_peek(MonkeyToken.LBRACE):
            return None
        #
        e.consequence = self.parse_block_statement()
        #
        if self.peek_token_is(MonkeyToken.ELSE):
            self.next_token()
            #
            if not self.expect_peek(MonkeyToken.LBRACE):
                return None
            e.alternative = self.parse_block_statement()
        #
        return e

    def parse_function_literal(self):
        lit = MonkeyFunctionLiteral()
        lit.token = self.cur_token
        #
        if not self.expect_peek(MonkeyToken.LPAREN):
            return None
        #
        lit.parameters = self.parse_function_parameters()
        #
        if not self.expect_peek(MonkeyToken.LBRACE):
            return None
        #
        lit.body = self.parse_block_statement()
        #
        return lit

    def parse_function_parameters(self):
        identifiers = []
        #
        if self.peek_token_is(MonkeyToken.RPAREN):
            self.next_token()
            return identifiers
        #
        self.next_token()
        ident = MonkeyIdentifier()
        ident.token = self.cur_token
        ident.value = self.cur_token.literal
        identifiers.append(ident)
        #
        while self.peek_token_is(MonkeyToken.COMMA):
            self.next_token()
            self.next_token()
            ident = MonkeyIdentifier()
            ident.token = self.cur_token
            ident.value = self.cur_token.literal
            identifiers.append(ident)
        #
        if not self.expect_peek(MonkeyToken.RPAREN):
            return None
        #
        return identifiers

    def parse_call_expression(self, function):
        exp = MonkeyCallExpression()
        exp.token = self.cur_token
        exp.function = function
        exp.arguments = self.parse_expression_list(MonkeyToken.RPAREN)
        return exp

    def parse_expression_list(self, end):
        ret = []
        #
        if self.peek_token_is(end):
            self.next_token()
            return ret
        #
        self.next_token()
        ret.append(self.parse_expression(self.LOWEST))
        #
        while self.peek_token_is(MonkeyToken.COMMA):
            self.next_token()
            self.next_token()
            ret.append(self.parse_expression(self.LOWEST))
        #
        if not self.expect_peek(end):
            return None
        #
        return ret
    
    def parse_index_expression(self, left):
        exp = MonkeyIndexExpression()
        exp.token = self.cur_token
        exp.left = left
        #
        self.next_token()
        exp.index = self.parse_expression(self.LOWEST)
        #
        if not self.expect_peek(MonkeyToken.RBRACKET):
            return None
        #
        return exp

    def cur_token_is(self, t):
        return self.cur_token.type == t

    def peek_token_is(self, t):
        return self.peek_token.type == t

    def expect_peek(self, t):
        if self.peek_token_is(t):
            self.next_token()
            return True
        else:
            self.peek_error(t)
            return False

    def peek_error(self, t):
        m = 'expected next token to be %s, got %s instead' %(
                t, self.peek_token.type
            )
        self.errors.append(m)

    def register_prefix(self, token_type, fn):
        self.prefix_parse_fns[token_type] = fn

    def register_infix(self, token_type, fn):
        self.infix_parse_fns[token_type] = fn

    def no_prefix_parse_fn_error(self, token_type):
        m = 'no prefix parse function for %s found' %(token_type)
        self.errors.append(m)

    def peek_precedence(self):
        p = self.PRECEDENCES.get(self.peek_token.type)
        if p:
            return p
        #
        return self.LOWEST

    def cur_precedence(self):
        p = self.PRECEDENCES.get(self.cur_token.type)
        if p:
            return p
        #
        return self.LOWEST

    def new(l):
        p = MonkeyParser()
        p.lexer = l
        p.next_token()
        p.next_token()
        return p
    new = staticmethod(new)


class MonkeyProgram(MonkeyNode):
    def __init__(self):
        self.statements = []

    def token_literal(self):
        if len(self.statements) > 0:
            return self.statements[0].token_literal()
        else:
            return ''
    
    def string(self):
        ret = ''
        for s in self.statements:
            ret += s.string()
        return ret


class MonkeyHashable:
    def hash_key(self):
        pass


class MonkeyObject:
    INTEGER_OBJ = 'INTEGER'
    BOOLEAN_OBJ = 'BOOLEAN'
    NULL_OBJ = 'NULL'
    RETURN_VALUE_OBJ = 'RETURN_VALUE'
    ERROR_OBJ = 'ERROR'
    FUNCTION_OBJ = 'FUNCTION'
    STRING_OBJ = 'STRING'
    BUILTIN_OBJ = 'BUILTIN'
    ARRAY_OBJ = 'ARRAY'
    HASH_OBJ = 'HASH'

    def __init__(self, value=None, type_=''):
        self.value = value
        self.object_type = type_

    def type(self):
        return self.object_type

    def inspect(self):
        return ''

    def inspect_value(self):
        return self.inspect()


class MonkeyObjectInteger(MonkeyObject, MonkeyHashable):
    def type(self):
        return self.INTEGER_OBJ

    def inspect(self):
        return '%s' %(self.value)

    def hash_key(self):
        o = MonkeyHashKey(type_=self.type(), value=self.value)
        return o


class MonkeyObjectString(MonkeyObject, MonkeyHashable):
    def type(self):
        return self.STRING_OBJ

    def inspect(self):
        return '"%s"' %(self.value)

    def hash_key(self):
        o = MonkeyHashKey(type_=self.type(), value=hash(self.value))
        return o

    def inspect_value(self):
        return self.value


class MonkeyObjectBoolean(MonkeyObject, MonkeyHashable):
    def type(self):
        return self.BOOLEAN_OBJ

    def inspect(self):
        ret = '%s' %(self.value)
        ret = ret.lower()
        return ret
    
    def hash_key(self):
        o = MonkeyHashKey(type_=self.type())
        if self.value:
            o.value = 1
        else:
            o.value = 0
        return o


class MonkeyObjectNull(MonkeyObject):
    def type(self):
        return self.NULL_OBJ

    def inspect(self):
        return 'null'


class MonkeyObjectReturnValue(MonkeyObject):
    def type(self):
        return self.RETURN_VALUE_OBJ

    def inspect(self):
        return self.value.inspect()


class MonkeyObjectError(MonkeyObject):
    def __init__(self, value=None, message=''):
        self.message = message
        self.value = value

    def type(self):
        return self.ERROR_OBJ

    def inspect(self):
        return 'ERROR: %s' %(self.message)


class MonkeyObjectFunction(MonkeyObject):
    def __init__(self):
        self.parameters = []
        self.body = MonkeyBlockStatement()
        self.env = MonkeyEnvironment.new()

    def type(self):
        return self.FUNCTION_OBJ

    def inspect(self):
        params = []
        for p in self.parameters:
            params.append(p.string())
        #
        ret = 'fn'
        ret += '('
        ret += ', '.join(params)
        ret += ')'
        ret += self.body.string()
        #
        return ret


class MonkeyObjectBuiltin(MonkeyObject):
    def __init__(self, fn=None, value=None):
        self.fn = fn
        self.value = value

    def type(self):
        return self.BUILTIN_OBJ

    def inspect(self):
        return 'builtin function'


class MonkeyObjectArray(MonkeyObject):
    def __init__(self):
        self.elements = []

    def type(self):
        return self.ARRAY_OBJ

    def inspect(self):
        elements = []
        for e in self.elements:
            elements.append(e.inspect())
        #
        ret = '['
        ret += ', '.join(elements)
        ret += ']'
        #
        return ret


class MonkeyObjectHash(MonkeyObject):
    def __init__(self):
        self.pairs = {}

    def type(self):
        return self.HASH_OBJ

    def inspect(self):
        pairs = []
        for k in self.pairs.keys():
            v = self.pairs.get(k)
            pair = '%s: %s' %(v.key.inspect(), v.value.inspect())
            pairs.append(pair)
        #
        ret = '{'
        ret += ', '.join(pairs)
        ret += '}'
        #
        return ret


class MonkeyHashKey:
    def __init__(self, type_='', value=None):
        self.type = type_
        self.value = value

    def __eq__(self, other):
        if isinstance(other, MonkeyHashKey):
            if other.type == self.type and other.value == self.value:
                return True
        return False

    def __ne__(self, other):
        if isinstance(other, MonkeyHashKey):
            if other.type == self.type and other.value == self.value:
                return False
        return True
    
    def __hash__(self):
        h = '%s-%s' %(self.type, self.value)
        return hash(h)


class MonkeyHashPair:
    def __init__(self):
        self.key = MonkeyObject()
        self.value = MonkeyObject()


class MonkeyEnvironment:
    def __init__(self, outer=None):
        self.store = {}
        self.outer = outer

    def get(self, name):
        obj = self.store.get(name)
        if obj is None and self.outer is not None:
            obj = self.outer.get(name)
        return obj

    def set(self, name, value):
        self.store[name] = value
        return value

    def debug(self):
        for k in self.store.keys():
            v = self.store.get(k)
            if v is not None:
                Monkey.output('%s: %s' %(
                        k,
                        v.inspect(),
                    )
                )

    def new():
        e = MonkeyEnvironment()
        return e
    new = staticmethod(new)

    def new_enclosed(outer):
        e = MonkeyEnvironment()
        e.outer = outer
        return e
    new_enclosed = staticmethod(new_enclosed)

    def from_dictionary(d):
        e = MonkeyEnvironment()
        if not isinstance(d, dict):
            return e
        #
        for k in d.keys():
            v = d.get(k)
            key = None
            value = None
            if type(k) == type(''):
                key = k
            else:
                key = str(k)
            #
            if type(v) == type(''):
                value = MonkeyObjectString(value=v)
            elif type(v) == type(1):
                value = MonkeyObjectInteger(value=v)
            elif type(v) == type(True):
                value = MonkeyObjectBoolean(value=v)
            else:
                value = MonkeyObjectString(value=str(v))
            #
            if key is not None and value is not None:
                e.set(key, value)
        return e
    from_dictionary = staticmethod(from_dictionary)


class MonkeyBuiltinFunctions:
    def len(evaluator, args):
        if len(args) != 1:
            return evaluator.new_error(
                'wrong number of arguments, got=%s, want=1' %(
                    len(args),
                )
            )
        #
        a = args[0]
        if isinstance(a, MonkeyObjectString):
            o = MonkeyObjectInteger()
            o.value = len(a.value)
            return o
        elif isinstance(a, MonkeyObjectArray):
            o = MonkeyObjectInteger()
            o.value = len(a.elements)
            return o
        else:
            return evaluator.new_error(
                'argument to "len" not supported, got %s' %(
                    a.type()       
                )
            )
    len = staticmethod(len)

    def first(evaluator, args):
        if len(args) != 1:
            return evaluator.new_error(
                'wrong number of arguments, got=%s, want=1' %(
                    len(args),
                )
            )
        #
        a = args[0]
        if not isinstance(a, MonkeyObjectArray):
            return evaluator.new_error(
                'argument to "first" must be ARRAY, got %s' %(
                    a.type()       
                )
            )
        #
        if len(a.elements) > 0:
            return a.elements[0]
        #
        return evaluator.NULL
    first = staticmethod(first)

    def last(evaluator, args):
        if len(args) != 1:
            return evaluator.new_error(
                'wrong number of arguments, got=%s, want=1' %(
                    len(args),
                )
            )
        #
        a = args[0]
        if not isinstance(a, MonkeyObjectArray):
            return evaluator.new_error(
                'argument to "last" must be ARRAY, got %s' %(
                    a.type()       
                )
            )
        #
        length = len(a.elements)
        if length > 0:
            return a.elements[length-1]
        #
        return evaluator.NULL
    last = staticmethod(last)

    def rest(evaluator, args):
        if len(args) != 1:
            return evaluator.new_error(
                'wrong number of arguments, got=%s, want=1' %(
                    len(args),
                )
            )
        #
        a = args[0]
        if not isinstance(a, MonkeyObjectArray):
            return evaluator.new_error(
                'argument to "rest" must be ARRAY, got %s' %(
                    a.type()       
                )
            )
        #
        length = len(a.elements)
        if length > 0:
            o = MonkeyObjectArray()
            o.elements = a.elements[1:]
            return o
        #
        return evaluator.NULL
    rest = staticmethod(rest)

    def push(evaluator, args):
        if len(args) != 2:
            return evaluator.new_error(
                'wrong number of arguments, got=%s, want=2' %(
                    len(args),
                )
            )
        #
        a = args[0]
        if not isinstance(a, MonkeyObjectArray):
            return evaluator.new_error(
                'argument to "push" must be ARRAY, got %s' %(
                    a.type()       
                )
            )
        #
        o = MonkeyObjectArray()
        o.elements = a.elements[:]
        o.elements.append(args[1])
        return o
    push = staticmethod(push)

    def puts(evaluator, args):
        for a in args:
            Monkey.output(a.inspect_value(), evaluator.output)
        #
        return evaluator.NULL
    puts = staticmethod(puts)


class MonkeyBuiltins:
    BUILTINS = {
        'len': MonkeyObjectBuiltin(MonkeyBuiltinFunctions.len),
        'first': MonkeyObjectBuiltin(MonkeyBuiltinFunctions.first),
        'last': MonkeyObjectBuiltin(MonkeyBuiltinFunctions.last),
        'rest': MonkeyObjectBuiltin(MonkeyBuiltinFunctions.rest),
        'push': MonkeyObjectBuiltin(MonkeyBuiltinFunctions.push),
        'puts': MonkeyObjectBuiltin(MonkeyBuiltinFunctions.puts),
    }

    def get(f):
        return MonkeyBuiltins.BUILTINS.get(f)
    get = staticmethod(get)


class MonkeyEvaluator:
    NULL = MonkeyObjectNull()
    TRUE = MonkeyObjectBoolean(True)
    FALSE = MonkeyObjectBoolean(False)

    def __init__(self):
        self.output = sys.stdout

    def eval(self, node, env):
        if isinstance(node, MonkeyProgram):
            return self.eval_program(node, env)
        elif isinstance(node, MonkeyExpressionStatement):
            return self.eval(node.expression, env)
        elif isinstance(node, MonkeyIntegerLiteral):
            o = MonkeyObjectInteger()
            o.value = node.value
            return o
        elif isinstance(node, MonkeyBoolean):
            return self.get_boolean(node.value)
        elif isinstance(node, MonkeyPrefixExpression):
            right = self.eval(node.right, env)
            if self.is_error(right):
                return right
            #
            return self.eval_prefix_expression(node.operator, right)
        elif isinstance(node, MonkeyInfixExpression):
            left = self.eval(node.left, env) 
            if self.is_error(left):
                return left
            #
            right = self.eval(node.right, env)
            if self.is_error(right):
                return right
            #
            return self.eval_infix_expression(node.operator, left, right)
        elif isinstance(node, MonkeyBlockStatement):
            return self.eval_block_statement(node, env)
        elif isinstance(node, MonkeyIfExpression):
            return self.eval_if_expression(node, env)
        elif isinstance(node, MonkeyReturnStatement):
            val = self.eval(node.return_value, env)
            if self.is_error(val):
                return val
            #
            o = MonkeyObjectReturnValue()
            o.value = val
            return o
        elif isinstance(node, MonkeyLetStatement):
            val = self.eval(node.value, env)
            if self.is_error(val):
                return val
            #
            env.set(node.name.value, val)
        elif isinstance(node, MonkeyIdentifier):
            return self.eval_identifier(node, env)
        elif isinstance(node, MonkeyFunctionLiteral):
            params = node.parameters
            body = node.body
            #
            o = MonkeyObjectFunction()
            o.parameters = params
            o.body = body
            o.env = env
            return o
        elif isinstance(node, MonkeyCallExpression):
            function = self.eval(node.function, env)
            if self.is_error(function):
                return function
            #
            args = self.eval_expressions(node.arguments, env)
            if len(args) == 1 and self.is_error(args[0]):
                return args[0]
            #
            return self.apply_function(function, args)
        elif isinstance(node, MonkeyStringLiteral):
            o = MonkeyObjectString()
            o.value = node.value
            return o
        elif isinstance(node, MonkeyArrayLiteral):
            elements = self.eval_expressions(node.elements, env)
            if len(elements) == 1 and self.is_error(elements[0]):
                return elements[0]
            #
            o = MonkeyObjectArray()
            o.elements = elements
            return o
        elif isinstance(node, MonkeyIndexExpression):
            left = self.eval(node.left, env)
            if self.is_error(left):
                return left
            #
            index = self.eval(node.index, env)
            if self.is_error(index):
                return index
            #
            return self.eval_index_expression(left, index)
        elif isinstance(node, MonkeyHashLiteral):
            return self.eval_hash_literal(node, env)
        #
        return None

    def eval_program(self, program, env):
        ret = MonkeyObject()
        for s in program.statements:
            ret = self.eval(s, env)
            #
            if isinstance(ret, MonkeyObjectReturnValue):
                return ret.value
            elif isinstance(ret, MonkeyObjectError):
                return ret
        #
        return ret

    def eval_block_statement(self, block, env):
        ret = MonkeyObject()
        for s in block.statements:
            ret = self.eval(s, env)
            #
            if ret:
                rt = ret.type()
                if rt == MonkeyObject.RETURN_VALUE_OBJ or \
                    rt == MonkeyObject.ERROR_OBJ:
                    return ret
        #
        return ret
    
    def get_boolean(self, val):
        if val:
            return self.TRUE
        #
        return self.FALSE

    def eval_prefix_expression(self, operator, right):
        if operator == '!':
            return self.eval_bang_operator_expression(right)
        elif operator == '-':
            return self.eval_minus_prefix_operator_expression(right)
        return self.new_error('unknown operator: %s%s' %(
            operator, right.type()))

    def eval_infix_expression(self, operator, left, right):
        if left.type() == MonkeyObject.INTEGER_OBJ and \
            right.type() == MonkeyObject.INTEGER_OBJ:
            return self.eval_integer_infix_expression(operator, left, right)
        elif left.type() == MonkeyObject.STRING_OBJ and \
            right.type() == MonkeyObject.STRING_OBJ:
            return self.eval_string_infix_expression(operator, left, right)
        elif operator == '==':
            return self.get_boolean(left == right)
        elif operator == '!=':
            return self.get_boolean(left != right)
        elif left.type() != right.type():
            return self.new_error('type mismatch: %s %s %s' %(
                left.type(), operator, right.type()))
        return self.new_error('unknown operator: %s %s %s' %(
            left.type(), operator, right.type()))

    def eval_integer_infix_expression(self, operator, left, right):
        left_val = left.value
        right_val = right.value
        #
        o = MonkeyObjectInteger()
        if operator == '+':
            o.value = left_val + right_val
            return o
        elif operator == '-':
            o.value = left_val - right_val
            return o
        elif operator == '*':
            o.value = left_val * right_val
            return o
        elif operator == '/':
            try:
                o.value = left_val // right_val
                return o
            except:
                return self.NULL
        elif operator == '<':
            return self.get_boolean(left_val < right_val)
        elif operator == '>':
            return self.get_boolean(left_val > right_val)
        elif operator == '==':
            return self.get_boolean(left_val == right_val)
        elif operator == '!=':
            return self.get_boolean(left_val != right_val)
        return self.new_error('unknown operator: %s %s %s' %(
            left.type(), operator, right.type()))

    def eval_string_infix_expression(self, operator, left, right):
        left_val = left.value
        right_val = right.value
        #
        o = MonkeyObjectString()
        if operator != '+':
            return self.new_error('unknown operator: %s %s %s' %(
                left.type(), operator, right.type()))
        #
        o.value = left_val + right_val
        return o

    def eval_bang_operator_expression(self, right):
        if right == self.TRUE:
            return self.FALSE
        elif right == self.FALSE:
            return self.TRUE
        elif right == self.NULL:
            return self.TRUE
        return self.FALSE

    def eval_minus_prefix_operator_expression(self, right):
        if right.type() != MonkeyObject.INTEGER_OBJ:
            return self.new_error('unknown operator: -%s' %(right.type()))
        #
        val = right.value
        ret = MonkeyObjectInteger()
        ret.value = -val
        #
        return ret

    def eval_if_expression(self, expression, env):
        condition = self.eval(expression.condition, env)
        if self.is_error(condition):
            return condition
        #
        if self.is_truthy(condition):
            return self.eval(expression.consequence, env)
        elif not expression.alternative.is_empty():
            return self.eval(expression.alternative, env)
        else:
            return self.NULL

    def eval_identifier(self, node, env):
        val = env.get(node.value)
        if val:
            return val
        #
        builtin = MonkeyBuiltins.get(node.value)
        if builtin:
            return builtin
        #
        return self.new_error('identifier not found: %s' %(node.value))
    
    def eval_expressions(self, exp, env):
        result = []
        #
        for e in exp:
            evaluated = self.eval(e, env)
            if self.is_error(evaluated):
                result.append(evaluated)
                return result
            result.append(evaluated)
        #
        return result

    def eval_index_expression(self, left, index):
        if left.type() == MonkeyObject.ARRAY_OBJ and \
            index.type() == MonkeyObject.INTEGER_OBJ:
            return self.eval_array_index_expression(left, index)
        elif left.type() == MonkeyObject.HASH_OBJ:
            return self.eval_hash_index_expression(left, index)
        return self.new_error('index operator not supported: %s' %(
            left.type()))

    def eval_array_index_expression(self, array, index):
        idx = index.value
        max_index = len(array.elements) - 1
        #
        if idx < 0 or idx > max_index:
            return MonkeyEvaluator.NULL
        #
        return array.elements[idx]

    def eval_hash_literal(self, node, env):
        pairs = {}
        #
        for k in node.pairs.keys():
            key = self.eval(k, env)
            if self.is_error(key):
                return key
            #
            if not isinstance(key, MonkeyHashable):
                return self.new_error('unusable as hash key: %s' %(
                        key.type()
                    )
                )
            #
            v = node.pairs.get(k)
            val = self.eval(v, env)
            if self.is_error(val):
                return val
            #
            hashed = key.hash_key()
            p = MonkeyHashPair()
            p.key = key
            p.value = val
            pairs[hashed] = p
        #
        o = MonkeyObjectHash()
        o.pairs = pairs
        #
        return o

    def eval_hash_index_expression(self, hashtable, index):
        if not isinstance(index, MonkeyHashable):
            return self.new_error('unusable as hash key: %s' %(
                    index.type()
                )
            )
        #
        pair = hashtable.pairs.get(index.hash_key())
        if pair is None:
            return self.NULL
        #
        return pair.value

    def apply_function(self, fn, args):
        if isinstance(fn, MonkeyObjectFunction):
            extended_env = self.extend_function_env(fn, args)
            evaluated = self.eval(fn.body, extended_env)
            return self.unwrap_return_value(evaluated)
        elif isinstance(fn, MonkeyObjectBuiltin):
            return fn.fn(self, args)
        #
        return self.new_error('not a function: %s' %(fn.type()))

    def extend_function_env(self, fn, args):
        env = MonkeyEnvironment.new_enclosed(fn.env)
        for p in range(len(fn.parameters)):
            param = fn.parameters[p] 
            env.set(param.value, args[p])
        #
        return env

    def unwrap_return_value(self, obj):
        if isinstance(obj, MonkeyObjectReturnValue):
            return obj.value
        #
        return obj

    def is_truthy(self, obj):
        if obj == self.NULL:
            return False
        elif obj == self.TRUE:
            return True
        elif obj == self.FALSE:
            return False
        else:
            return True

    def new_error(self, message):
        ret = MonkeyObjectError()
        ret.message = message
        return ret
   
    def is_error(self, obj):
        if obj:
            return obj.type() == MonkeyObject.ERROR_OBJ
        #
        return False

    def new():
        e = MonkeyEvaluator()
        return e
    new = staticmethod(new)


class Monkey:
    PROMPT = '>> '

    def input(s):
        try:
            return raw_input(s)
        except:
            return input(s)
    input = staticmethod(input)

    def output(s, f=sys.stdout):
        try:
            f.write('%s%s' %(s, MONKEYPY_LINESEP))
        except:
            pass
    output = staticmethod(output)

    def lexer():
        Monkey.output(MONKEYPY_TITLE)
        Monkey.output(MONKEYPY_MESSAGE)
        while True:
            inp = Monkey.input(Monkey.PROMPT).strip()
            if not inp:
                break
            l = MonkeyLexer.new(inp)
            while True:
                t = l.next_token()
                if t.type == MonkeyToken.EOF:
                    break
                Monkey.output(
                    'Type: %s, Literal: %s' %(t.type, t.literal))
    lexer = staticmethod(lexer)

    def parser():
        Monkey.output(MONKEYPY_TITLE)
        Monkey.output(MONKEYPY_MESSAGE)
        while True:
            inp = Monkey.input(Monkey.PROMPT).strip()
            if not inp:
                break
            l = MonkeyLexer.new(inp)
            p = MonkeyParser.new(l)
            program = p.parse_program()
            #
            if p.errors:
                Monkey.print_parse_errors(p.errors)
                continue
            #
            Monkey.output(program.string())
    parser = staticmethod(parser)

    def print_parse_errors(e, output=sys.stdout):
        for i in e:
            Monkey.output('PARSER ERROR: %s' %(i), output)
    print_parse_errors = staticmethod(print_parse_errors)

    def evaluator():
        Monkey.output(MONKEYPY_TITLE)
        Monkey.output(MONKEYPY_MESSAGE)
        env = MonkeyEnvironment.new()
        while True:
            inp = Monkey.input(Monkey.PROMPT).strip()
            if not inp:
                break
            l = MonkeyLexer.new(inp)
            p = MonkeyParser.new(l)
            program = p.parse_program()
            #
            if p.errors:
                Monkey.print_parse_errors(p.errors)
                continue
            #
            evaluator = MonkeyEvaluator.new()
            evaluated = evaluator.eval(program, env)
            if evaluated:
                Monkey.output(evaluated.inspect())
    evaluator = staticmethod(evaluator)

    def evaluator_string(s, environ=None, output=sys.stdout):
        if environ is None or not isinstance(environ, MonkeyEnvironment):
            env = MonkeyEnvironment.new()
        else:
            env = environ
        l = MonkeyLexer.new(s)
        p = MonkeyParser.new(l)
        program = p.parse_program()
        #
        if p.errors:
            Monkey.print_parse_errors(p.errors, output)
            return
        #
        evaluator = MonkeyEvaluator.new()
        evaluator.output = output
        evaluated = evaluator.eval(program, env)
        if evaluated:
            Monkey.output(evaluated.inspect(), output)
    evaluator_string = staticmethod(evaluator_string)

    def main(argv):
        if len(argv) < 2:
            Monkey.evaluator()
        else:
            t = argv[1]
            s = t
            if os.path.exists(t):
                try:
                    s = open(t).read()
                except:
                    pass
            #
            if s:
                Monkey.evaluator_string(s)
    main = staticmethod(main)


if __name__ == '__main__':
    Monkey.main(sys.argv)


