from monkey import *

# helper functions
def check_parser_errors(p):
    errors = p.errors
    if not errors:
        return
    #
    print('Parser has %s errors' %(len(errors)))
    for e in errors:
        print('\terror: %s' %(e))

def test_integer_literal(operand, val):
    if operand.value != val:
        print('operand.value not %s, got %s' %(val, operand.value))
        return False
    #
    if operand.token_literal() != '%s' %val:
        print('operand.token_literal() not %s, got %s' %(
                val, operand.token_literal()
            )
        )
        return False
    #
    return True

def test_boolean_literal(operand, val):
    if operand.value != val:
        print('operand.value not %s, got %s' %(val, operand.value))
        return False
    #
    if operand.token_literal() != '%s' %str(val).lower():
        print('operand.token_literal() not %s, got %s' %(
                val, operand.token_literal()
            )
        )
        return False
    #
    return True

def test_identifier(e, val):
    ident = e
    if ident.value != val:
        print('ident.value not %s, got %s' %(val, ident.value))
        return False
    #
    if ident.token_literal() != '%s' %val:
        print('ident.token_literal() not %s, got %s' %(
                val, ident.token_literal()
            )
        )
        return False
    #
    return True

def test_literal_expression(e, expected):
    if type(expected) == type(1):
        return test_integer_literal(e, expected)
    elif type(expected) == type(''):
        return test_identifier(e, expected)
    elif type(expected) == type(True):
        return test_boolean_literal(e, expected)
    print('type of e not handled, got %s' %(e))
    return False

def test_infix_expression(exp, left, operator, right):
    if not test_literal_expression(exp.left, left):
        return False
    if exp.operator != operator:
        print('exp.operator is not %s, got %s' %(operator, exp.operator))
        return False
    if not test_literal_expression(exp.right, right):
        return False
    return True

def test_eval(inp):
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)
    program = p.parse_program()
    env = MonkeyEnvironment.new()
    evaluator = MonkeyEvaluator.new()
    return evaluator.eval(program, env)

def test_integer_object(obj, expected):
    if obj.value != expected:
        print('object has wrong value, got %s, want %s' %(
                obj.value, expected
            )
        )
        return False
    return True

def test_boolean_object(obj, expected):
    if obj.value != expected:
        print('object has wrong value, got %s, want %s' %(
                obj.value, expected
            )
        )
        return False
    return True

def test_null_object(expected):
    if expected != MonkeyEvaluator.NULL:
        print('object is not NULL, got %s' %(expected))
        return False
    return True

# tests
def test_next_token_1():
    inp = '=+(){},;'
    l = MonkeyLexer.new(inp)
    tests = [
            [MonkeyToken.ASSIGN, '='],
            [MonkeyToken.PLUS, '+'],
            [MonkeyToken.LPAREN, '('],
            [MonkeyToken.RPAREN, ')'],
            [MonkeyToken.LBRACE, '{'],
            [MonkeyToken.RBRACE, '}'],
            [MonkeyToken.COMMA, ','],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.EOF, '']
        ]
    for t in tests:
        token = l.next_token()
        if token.type != t[0]:
            print('ERROR TYPE: expected %s, got %s' %(t[0], token.type))
        if token.literal != t[1]:
            print('ERROR LITERAL: expected %s, got %s' %(t[1], token.literal))

def test_next_token_2():
    inp = '''let five = 5;
let ten = 10;
let add = fn(x, y) {
    x + y;
};
let result = add(five, ten);

! - / * 5;
5 < 10 > 5;

if (5 < 10) {
    return true;
} else {
    return false;
}

10 == 10;
10 != 9;
"foobar"
"foo bar"
[1,2];
{"foo": "bar"}
'''
    l = MonkeyLexer.new(inp)
    tests = [
            [MonkeyToken.LET, 'let'],
            [MonkeyToken.IDENT, 'five'],
            [MonkeyToken.ASSIGN, '='],
            [MonkeyToken.INT, '5'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.LET, 'let'],
            [MonkeyToken.IDENT, 'ten'],
            [MonkeyToken.ASSIGN, '='],
            [MonkeyToken.INT, '10'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.LET, 'let'],
            [MonkeyToken.IDENT, 'add'],
            [MonkeyToken.ASSIGN, '='],
            [MonkeyToken.FUNCTION, 'fn'],
            [MonkeyToken.LPAREN, '('],
            [MonkeyToken.IDENT, 'x'],
            [MonkeyToken.COMMA, ','],
            [MonkeyToken.IDENT, 'y'],
            [MonkeyToken.RPAREN, ')'],
            [MonkeyToken.LBRACE, '{'],
            [MonkeyToken.IDENT, 'x'],
            [MonkeyToken.PLUS, '+'],
            [MonkeyToken.IDENT, 'y'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.RBRACE, '}'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.LET, 'let'],
            [MonkeyToken.IDENT, 'result'],
            [MonkeyToken.ASSIGN, '='],
            [MonkeyToken.IDENT, 'add'],
            [MonkeyToken.LPAREN, '('],
            [MonkeyToken.IDENT, 'five'],
            [MonkeyToken.COMMA, ','],
            [MonkeyToken.IDENT, 'ten'],
            [MonkeyToken.RPAREN, ')'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.BANG, '!'],
            [MonkeyToken.MINUS, '-'],
            [MonkeyToken.SLASH, '/'],
            [MonkeyToken.ASTERISK, '*'],
            [MonkeyToken.INT, '5'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.INT, '5'],
            [MonkeyToken.LT, '<'],
            [MonkeyToken.INT, '10'],
            [MonkeyToken.GT, '>'],
            [MonkeyToken.INT, '5'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.IF, 'if'],
            [MonkeyToken.LPAREN, '('],
            [MonkeyToken.INT, '5'],
            [MonkeyToken.LT, '<'],
            [MonkeyToken.INT, '10'],
            [MonkeyToken.RPAREN, ')'],
            [MonkeyToken.LBRACE, '{'],
            [MonkeyToken.RETURN, 'return'],
            [MonkeyToken.TRUE, 'true'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.RBRACE, '}'],
            [MonkeyToken.ELSE, 'else'],
            [MonkeyToken.LBRACE, '{'],
            [MonkeyToken.RETURN, 'return'],
            [MonkeyToken.FALSE, 'false'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.RBRACE, '}'],
            [MonkeyToken.INT, '10'],
            [MonkeyToken.EQ, '=='],
            [MonkeyToken.INT, '10'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.INT, '10'],
            [MonkeyToken.NOT_EQ, '!='],
            [MonkeyToken.INT, '9'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.STRING, 'foobar'],
            [MonkeyToken.STRING, 'foo bar'],
            [MonkeyToken.LBRACKET, '['],
            [MonkeyToken.INT, '1'],
            [MonkeyToken.COMMA, ','],
            [MonkeyToken.INT, '2'],
            [MonkeyToken.RBRACKET, ']'],
            [MonkeyToken.SEMICOLON, ';'],
            [MonkeyToken.LBRACE, '{'],
            [MonkeyToken.STRING, 'foo'],
            [MonkeyToken.COLON, ':'],
            [MonkeyToken.STRING, 'bar'],
            [MonkeyToken.RBRACE, '}'],
            [MonkeyToken.EOF, ''],
        ]
    for t in tests:
        token = l.next_token()
        if token.type != t[0]:
            print('ERROR TYPE: expected %s, got %s' %(t[0], token.type))
        if token.literal != t[1]:
            print('ERROR LITERAL: expected %s, got %s' %(t[1], token.literal))

def test_let_statements():
    def do_test(s, name):
        if s.token_literal() != 'let':
            print('token literal is not let, got %s' %(s.token_literal()))
            return False
        #
        if s.name.value != name:
            print('name.value != %s, got %s' %(
                name, 
                s.name.value,
                )
            )
        #
        if s.name.token_literal() != name:
            print('name != %s, got %s' %(
                name, 
                s.name,
                )
            )
        #
        return True

        

    inp = '''
let x = 5;
let y = 10;
let foobar = 838383;
'''
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)
    if not program:
        print('parse_program() returned None')
        return

    if len(program.statements) != 3:
        print('program.statements does not contain 3 statements, got %s'
            %(len(program.statements))
        )
        return
    tests = [
            'x',
            'y',
            'foobar'
        ]
    counter = 0
    for t in tests:
        s = program.statements[counter]
        if not do_test(s, t):
            return
        counter += 1

def test_return_statements():
    inp = '''
return 5;
return 10;
return 993322;
'''
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)
    if not program:
        print('parse_program() returned None')
        return

    if len(program.statements) != 3:
        print('program.statements does not contain 3 statements, got %s'
            %(len(program.statements))
        )
        return

    for s in program.statements:
        if s.token_literal() != 'return':
            print('token literal is not return, got %s' %(s.token_literal()))

def test_string():
    program = MonkeyProgram()
    let = MonkeyLetStatement()
    let_token = MonkeyToken()
    let_token.type = MonkeyToken.LET
    let_token.literal = 'let'
    let_name = MonkeyIdentifier()
    let_name.type = MonkeyToken.IDENT
    let_name.literal = 'myVar'
    let_name.value = 'myVar'
    let_value = MonkeyIdentifier()
    let_value.type = MonkeyToken.IDENT
    let_value.literal = 'anotherVar'
    let_value.value = 'anotherVar'
    let.token = let_token
    let.name = let_name
    let.value = let_value
    program.statements = [let]
    #
    if program.string() != 'let myVar = anotherVar;':
        print('program.string() wrong, got %s' %(program.string()))

def test_identifier_expression():
    inp = 'foobar;'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)
    if len(program.statements) != 1:
        print('program has not enough statements, got %s' %(
            len(program.statements)))
        return

    statement = program.statements[0]
    ident = statement.expression
    if ident.value != 'foobar':
        print('ident.value not foobar, got %s' %(ident.value))
    if ident.token_literal() != 'foobar':
        print('ident.value not foobar, got %s' %(ident.token_literal()))

def test_integer_literal_expression():
    inp = '5;'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)
    if len(program.statements) != 1:
        print('program has not enough statements, got %s' %(
            len(program.statements)))
        return

    statement = program.statements[0]
    literal = statement.expression
    if literal.value != 5:
        print('ident.value not 5, got %s' %(literal.value))
    if literal.token_literal() != '5':
        print('ident.value not 5, got %s' %(literal.token_literal()))

def test_parsing_prefix_expressions():
    tests = [
                ['!5;', '!', 5],
                ['-15;', '-', 15],
                ['!true;', '!', True],
                ['!false;', '!', False],
        ]
    for t in tests:
        inp = t[0]
        l = MonkeyLexer.new(inp)
        p = MonkeyParser.new(l)

        program = p.parse_program()
        check_parser_errors(p)

        if len(program.statements) != 1:
            print('program.statements does not contain 1 statements, got %s'
                %(len(program.statements))
            )
            return
        #
        statement = program.statements[0]
        exp = statement.expression

        op = t[1]
        if exp.operator != op:
            print('operator is not %s, got %s' %(op, exp.operator))
            return

        val = t[2]
        if not test_literal_expression(exp.right, val):
            return

def test_parsing_infix_expressions():
    tests = [
                ['5 + 5;', 5, '+', 5],
                ['5 - 5;', 5, '-', 5],
                ['5 * 5;', 5, '*', 5],
                ['5 / 5;', 5, '/', 5],
                ['5 > 5;', 5, '>', 5],
                ['5 < 5;', 5, '<', 5],
                ['5 == 5;', 5, '==', 5],
                ['5 != 5;', 5, '!=', 5],
                ['true == true;', True, '==', True],
                ['true != false;', True, '!=', False],
                ['false == false;', False, '==', False],
        ]
    for t in tests:
        inp = t[0]
        l = MonkeyLexer.new(inp)
        p = MonkeyParser.new(l)

        program = p.parse_program()
        check_parser_errors(p)

        if len(program.statements) != 1:
            print('program.statements does not contain 1 statements, got %s'
                %(len(program.statements))
            )
            return
        #
        statement = program.statements[0]
        exp = statement.expression

        left = t[1]
        if not test_literal_expression(exp.left, left):
            return

        op = t[2]
        if exp.operator != op:
            print('operator is not %s, got %s' %(op, exp.operator))
            return

        right = t[3]
        if not test_literal_expression(exp.right, right):
            return

def test_operator_precedence_parsing():
    tests = [
                [
                    '-a * b',
                    '((-a) * b)',
                ],
                [
                    '!-a',
                    '(!(-a))',
                ],
                [
                    'a + b + c',
                    '((a + b) + c)',
                ],
                [
                    'a + b - c',
                    '((a + b) - c)',
                ],
                [
                    'a * b * c',
                    '((a * b) * c)',
                ],
                [
                    'a * b / c',
                    '((a * b) / c)',
                ],
                [
                    'a + b / c',
                    '(a + (b / c))',
                ],
                [
                    'a + b * c + d / e - f',
                    '(((a + (b * c)) + (d / e)) - f)',
                ],
                [
                    '3 + 4; -5 * 5',
                    '(3 + 4)((-5) * 5)',
                ],
                [
                    '5 > 4 ==  3 < 4',
                    '((5 > 4) == (3 < 4))',
                ],
                [
                    '5 < 4 != 3 > 4',
                    '((5 < 4) != (3 > 4))',
                ],
                [
                    '3 + 4 * 5 == 3 * 1 + 4 * 5',
                    '((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))',
                ],
                [
                    '3 + 4 * 5 == 3 * 1 + 4 * 5',
                    '((3 + (4 * 5)) == ((3 * 1) + (4 * 5)))',
                ],
                [
                    'true',
                    'true'
                ],
                [
                    'false',
                    'false'
                ],
                [
                    '3 > 5 == false',
                    '((3 > 5) == false)'
                ],
                [
                    '3 < 5 == true',
                    '((3 < 5) == true)'
                ],
                [
                    '1 + (2 + 3) + 4',
                    '((1 + (2 + 3)) + 4)',
                ],
                [
                    '(5 + 5) * 2',
                    '((5 + 5) * 2)',
                ],
                [
                    '2 / (5 + 5)',
                    '(2 / (5 + 5))',
                ],
                [
                    '-(5 + 5)',
                    '(-(5 + 5))',
                ],
                [
                    '!(true == true)',
                    '(!(true == true))',
                ],
                [
                    'a + add(b * c) + d',
                    '((a + add((b * c))) + d)',
                ],
                [
                    'add(a, b, 1, 2 * 3, 4 + 5, add(6, 7 * 8))',
                    'add(a, b, 1, (2 * 3), (4 + 5), add(6, (7 * 8)))',
                ],
                [
                    'add(a + b + c * d / f + g)',
                    'add((((a + b) + ((c * d) / f)) + g))',
                ],
                [
                    'a * [1, 2, 3, 4][b * c] * d',
                    '((a * ([1, 2, 3, 4][(b * c)])) * d)',
                ],
                [
                    'add(a * b[2], b[1], 2 * [1, 2][1])',
                    'add((a * (b[2])), (b[1]), (2 * ([1, 2][1])))',
                ],
        ]
    for t in tests:
        inp = t[0]
        expected = t[1]
        l = MonkeyLexer.new(inp)
        p = MonkeyParser.new(l)

        program = p.parse_program()
        check_parser_errors(p)

        actual = program.string()

        if actual != expected:
            print('expected %s, got %s' %(expected, actual))

def test_boolean_literal_expression():
    inp = 'true;'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)
    if len(program.statements) != 1:
        print('program has not enough statements, got %s' %(
            len(program.statements)))
        return

    statement = program.statements[0]
    literal = statement.expression
    if literal.value != True:
        print('ident.value not True, got %s' %(literal.value))
    if literal.token_literal() != 'true':
        print('ident.value not true, got %s' %(literal.token_literal()))

def test_if_expression():
    inp = 'if (x < y) { x }'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    if len(program.statements) != 1:
        print('program.statements does not contain 1 statements, got %s'
            %(len(program.statements))
        )
        return

    statement = program.statements[0]
    exp = statement.expression
    if not test_infix_expression(exp.condition, 'x', '<', 'y'):
        return
    if len(exp.consequence.statements) != 1:
        print('consequence is not 1 statement, got %s'
            %(len(exp.consequence.statements))
        )
        return
    consequence = exp.consequence.statements[0]
    if not test_identifier(consequence.expression, 'x'):
        return
    if not exp.alternative.is_empty():
        print('alternative is not empty, got %s' %(exp.alternative))

def test_if_else_expression():
    inp = 'if (x < y) { x } else { y }'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    if len(program.statements) != 1:
        print('program.statements does not contain 1 statements, got %s'
            %(len(program.statements))
        )
        return

    statement = program.statements[0]
    exp = statement.expression
    if not test_infix_expression(exp.condition, 'x', '<', 'y'):
        return
    if len(exp.consequence.statements) != 1:
        print('consequence is not 1 statement, got %s'
            %(len(exp.consequence.statements))
        )
        return
    consequence = exp.consequence.statements[0]
    if not test_identifier(consequence.expression, 'x'):
        return
    if exp.alternative.is_empty():
        print('alternative is empty')
    if len(exp.alternative.statements) != 1:
        print('alternative is not 1 statement, got %s'
            %(len(exp.alternative.statements))
        )
        return
    alternative = exp.alternative.statements[0]
    if not test_identifier(alternative.expression, 'y'):
        return

def test_function_literal_parsing():
    inp = 'fn(x, y) { x + y; }'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    if len(program.statements) != 1:
        print('program.statements does not contain 1 statements, got %s'
            %(len(program.statements))
        )
        return

    statement = program.statements[0]
    function = statement.expression
    if len(function.parameters) != 2:
        print('function literal parameter wrong, want 2, got %s'
            %(len(function.parameters))
        )
        return
    test_literal_expression(function.parameters[0], 'x')
    test_literal_expression(function.parameters[1], 'y')

    if len(function.body.statements) != 1:
        print('function.body.statements has not 1 statement, got %s'
            %(len(function.body.statements))
        )
        return
    body = function.body.statements[0]
    test_infix_expression(body.expression, 'x', '+', 'y')

def test_function_parameter_parsing():
    tests = [
                ['fn() {};', []],
                ['fn(x) {};', ['x']],
                ['fn(x, y, z) {};', ['x', 'y', 'z']],
        ]
    for t in tests:
        inp = t[0]
        l = MonkeyLexer.new(inp)
        p = MonkeyParser.new(l)

        program = p.parse_program()
        check_parser_errors(p)

        statement = program.statements[0]
        function = statement.expression

        if len(function.parameters) != len(t[1]):
            print('length parameters wrong, want %s, got %s' %(
                    len(t[1]), len(function.parameters)
                )
            )
        for i in range(len(t[1])):
            test_literal_expression(function.parameters[i], t[1][i])

def test_call_expression_parsing():
    inp = 'add(1, 2 * 3, 4 + 5);'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    if len(program.statements) != 1:
        print('program.statements does not contain 1 statements, got %s'
            %(len(program.statements))
        )
        return

    statement = program.statements[0]
    exp = statement.expression
    if not test_identifier(exp.function, 'add'):
        return
    if len(exp.arguments) != 3:
        print('wrong length of arguments, got %s' %(len(exp.arguments)))
        return
    test_literal_expression(exp.arguments[0], 1)
    test_infix_expression(exp.arguments[1], 2, '*', 3)
    test_infix_expression(exp.arguments[2], 4, '+', 5)

def test_call_expression_parameter_parsing():
    tests = [
                ['add()', []],
                ['add(x)', ['x']],
                ['add(x, y, z)', ['x', 'y', 'z']],
        ]
    for t in tests:
        inp = t[0]
        l = MonkeyLexer.new(inp)
        p = MonkeyParser.new(l)

        program = p.parse_program()
        check_parser_errors(p)

        statement = program.statements[0]
        exp = statement.expression
        
        if len(exp.arguments) != len(t[1]):
            print('length parameters wrong, want %s, got %s' %(
                    len(t[1]), len(exp.arguments)
                )
            )
        for i in range(len(t[1])):
            test_literal_expression(exp.arguments[i], t[1][i])

def test_lets_statements_expression():
    tests = [
                ['let x = 5;', 'x', 5],
                ['let y = true;', 'y', True],
                ['let foobar = y;', 'foobar', 'y'],
        ]
    for t in tests:
        inp = t[0]
        l = MonkeyLexer.new(inp)
        p = MonkeyParser.new(l)

        program = p.parse_program()
        check_parser_errors(p)

        statement = program.statements[0]
        val = statement.value
        if not test_literal_expression(val, t[2]):
            print('value %s, expected %s' %(val, t[2]))

def test_eval_integer_expression():
    tests = [
                ['5', 5],
                ['10', 10],
                ['-5', -5],
                ['-10', -10],
                ['5 + 5 + 5 + 5 - 10', 10],
                ['2 * 2 * 2 * 2 * 2', 32],
                ['-50 + 100 - 50', 0],
                ['5 * 2 + 10', 20],
                ['5 + 2 * 10', 25],
                ['20 + 2 * -10', 0],
                ['50 / 2 * 2 + 10', 60],
                ['2 * (5 + 10)', 30],
                ['3 * 3 * 3 + 10', 37],
                ['3 * (3 * 3) + 10', 37],
                ['(5 + 10 * 2 + 15 / 3) * 2 + -10', 50],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        test_integer_object(evaluated, t[1])

def test_eval_boolean_expression():
    tests = [
                ['true', True],
                ['false', False],
                ['1 < 2', True],
                ['1 > 2', False],
                ['1 < 1', False],
                ['1 > 1', False],
                ['1 == 1', True],
                ['1 != 1', False],
                ['1 == 2', False],
                ['1 != 2', True],
                ['true == true', True],
                ['false == false', True],
                ['true == false', False],
                ['true != false', True],
                ['false != true', True],
                ['(1 < 2) == true', True],
                ['(1 < 2) == false', False],
                ['(1 > 2) == true', False],
                ['(1 > 2) == false', True],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        test_boolean_object(evaluated, t[1])

def test_bang_operator():
    tests = [
                ['!true', False],
                ['!false', True],
                ['!5', False],
                ['!!true', True],
                ['!!false', False],
                ['!!5', True],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        test_boolean_object(evaluated, t[1])

def test_if_else_expressions():
    tests = [
                ['if (true) {10}', 10],
                ['if (false) {10}', None],
                ['if (1) {10}', 10],
                ['if (1<2) {10}', 10],
                ['if (1>2) {10}', None],
                ['if (1>2) {10} else {20}', 20],
                ['if (1<2) {10} else {20}', 10],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        expected = t[1]
        if expected:
            test_integer_object(evaluated, expected)
        else:
            test_null_object(evaluated)

def test_return_statements_eval():
    tests = [
                ['return 10;', 10],
                ['return 10; 9; ', 10],
                ['return 2 * 5; 9;', 10],
                ['9; return 2 * 5; 9;', 10],
                ['if (10 > 1) { if (10 > 1) { return 10; } return 1;}', 10]
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        test_integer_object(evaluated, t[1])

def test_error_handling():
    tests = [
                [
                    '5 + true;',
                    'type mismatch: INTEGER + BOOLEAN',
                ],
                [
                    '5 + true; 5;',
                    'type mismatch: INTEGER + BOOLEAN',
                ],
                [
                    '-true;',
                    'unknown operator: -BOOLEAN',
                ],
                [
                    'true + false;',
                    'unknown operator: BOOLEAN + BOOLEAN',
                ],
                [
                    '5; true + false; 5',
                    'unknown operator: BOOLEAN + BOOLEAN',
                ],
                [
                    'if (10 > 1) { true + false; }',
                    'unknown operator: BOOLEAN + BOOLEAN',
                ],
                [
                    'if (10 > 1) { if (10 > 1) { return true + false; } return 1;}',
                    'unknown operator: BOOLEAN + BOOLEAN',
                ],
                [
                    'foobar',
                    'identifier not found: foobar',
                ],
                [
                    '"Hello" - "World"',
                    'unknown operator: STRING - STRING',
                ],
                [
                    '{"name": "monkey"}[fn(x) {x}];',
                    'unusable as hash key: FUNCTION',
                ]
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        if evaluated.message != t[1]:
            print('wrong error message, expected %s, got %s' %(
                    t[1], evaluated.message,
                )
            )

def test_let_statements_eval():
    tests = [
                ['let a = 5; a;', 5],
                ['let a = 5 * 5; a;', 25],
                ['let a = 5; let b = a; b;', 5],
                ['let a = 5; let b = a; let c = a + b + 5; c;', 15],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        test_integer_object(evaluated, t[1])

def test_function_object():
    inp = 'fn(x) { x + 2; };'
    evaluated = test_eval(inp)

    if len(evaluated.parameters) != 1:
        print('function has wrong parameter, got %s'
            %(len(evaluated.parameters))
        )
        return

    if evaluated.parameters[0].string() != 'x':
        print('parameter is not x, got %s' %(evaluated.parameter[0].string()))
        return

    expect_body = '{%s(x + 2);%s}' %(os.linesep, os.linesep)
    if evaluated.body.string().strip() != expect_body:
        print('body is not %s, got %s' %(
            expect_body, evaluated.body.string())
        )
        return

def test_function_application():
    tests = [
                ['let identity = fn(x) {x;}; identity(5);', 5],
                ['let identity = fn(x) {return x;}; identity(5)', 5],
                ['let double = fn(x) {x * 2;}; double(5);', 10],
                ['let add = fn(x, y) {x + y;}; add(5, 5);', 10],
                ['let add = fn(x, y) {x + y;}; add(5 + 5, add(5, 5));', 20],
                ['fn(x) {x;}(5)', 5],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        test_integer_object(evaluated, t[1])

def test_closures():
    inp = '''
        let newAdder = fn(x) {
            fn(y) {x + y};
        };

        let addTwo = newAdder(2);
        addTwo(2);
    '''
    test_integer_object(test_eval(inp), 4)

def test_string_literal_expression():
    inp = '"hello world";'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)
    if len(program.statements) != 1:
        print('program has not enough statements, got %s' %(
            len(program.statements)))
        return

    statement = program.statements[0]
    literal = statement.expression
    if literal.value != 'hello world':
        print('literal.value not "hello world", got "%s"' %(literal.value))

def test_string_literal():
    inp = '"hello world";'
    evaluated = test_eval(inp)
    if evaluated.value != 'hello world':
        print('string has wrong value, got "%s"' %(evaluated.value))
        return

def test_string_concatenation():
    inp = '"Hello" + " " + "World";'
    evaluated = test_eval(inp)
    if evaluated.value != 'Hello World':
        print('string has wrong value, got "%s"' %(evaluated.value))
        return

def test_builtin_functions():
    tests = [
                ['len("")', 0],
                ['len("four")', 4],
                ['len("hello world")', 11],
                ['len(1)', 'argument to "len" not supported, got INTEGER'],
                ['len("one", "two")', 'wrong number of arguments, got=2, want=1'],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        expected = t[1]
        if isinstance(expected, int):
            test_integer_object(evaluated, expected)
        elif isinstance(expected, str):
            if evaluated.message != expected:
                print('wrong error message, expected %s, got %s' %(
                        expected, evaluated.message,
                    )
                )

def test_parsing_array_literals():
    inp = '[1, 2 * 2, 3 + 3]'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    statement = program.statements[0]
    array = statement.expression
    if len(array.elements) != 3:
        print('len(array.elements) not 3, got "%s"' %(len(array.elements)))
    test_integer_literal(array.elements[0], 1)
    test_infix_expression(array.elements[1], 2, '*', 2)
    test_infix_expression(array.elements[2], 3, '+', 3)

def test_parsing_index_expressions():
    inp = 'myArray[1 + 1]'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    statement = program.statements[0]
    index = statement.expression
    test_identifier(index.left,'myArray')
    test_infix_expression(index.index, 1, '+', 1)

def test_array_literals():
    inp = '[1, 2 * 2, 3 + 3]'
    evaluated = test_eval(inp)
    if len(evaluated.elements) != 3:
        print('array has wrong num of elements, got %s' %(
            len(evaluated.elements))
        )
        return
    test_integer_object(evaluated.elements[0], 1)
    test_integer_object(evaluated.elements[1], 4)
    test_integer_object(evaluated.elements[2], 6)

def test_array_index_expressions():
    tests = [
                [
                    '[1,2,3][0]', 
                    1,
                ],
                [
                    '[1,2,3][1]', 
                    2,
                ],
                [
                    '[1,2,3][2]', 
                    3,
                ],
                [
                    'let i = 0; [1][i]', 
                    1,
                ],
                [
                    '[1,2,3][1+1]', 
                    3,
                ],
                [
                    'let myArray=[1,2,3]; myArray[2];', 
                    3,
                ],
                [
                    'let myArray=[1,2,3]; myArray[0]+myArray[1]+myArray[2];', 
                    6,
                ],
                [
                    'let myArray=[1,2,3]; let i=myArray[0]; myArray[i]', 
                    2,
                ],
                [
                    '[1,2,3][3]', 
                    None,
                ],
                [
                    '[1,2,3][-1]', 
                    None,
                ],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        expected = t[1]
        if expected:
            test_integer_object(evaluated, expected)
        else:
            test_null_object(evaluated)

def test_parsing_hash_literal_string_keys():
    inp = '{"one": 1, "two": 2, "three": 3}'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    statement = program.statements[0]
    e = statement.expression
    if len(e.pairs) != 3:
        print('hash pairs has wrong length, got "%s"' %(
            len(e.pairs)))
    expected = {'one': 1, 'two': 2, 'three': 3}
    for k in e.pairs.keys():
        v = e.pairs.get(k)
        expected_value = expected.get(k.string())
        test_integer_literal(v, expected_value)

def test_parsing_empty_hash_literal():
    inp = '{}'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    statement = program.statements[0]
    e = statement.expression
    if len(e.pairs) != 0:
        print('hash pairs has wrong length, got "%s"' %(
            len(e.pairs)))

def test_parsing_hash_literals_with_expressions():
    inp = '{"one": 0+1, "two": 10-8, "three": 15/5}'
    l = MonkeyLexer.new(inp)
    p = MonkeyParser.new(l)

    program = p.parse_program()
    check_parser_errors(p)

    statement = program.statements[0]
    e = statement.expression
    if len(e.pairs) != 3:
        print('hash pairs has wrong length, got "%s"' %(
            len(e.pairs)))
    expected = {
        'one': lambda x: test_infix_expression(x, 0, '+', 1),
        'two': lambda x: test_infix_expression(x, 10, '-', 8), 
        'three': lambda x: test_infix_expression(x, 15, '/', 5),
    }
    for k in e.pairs.keys():
        v = e.pairs.get(k)
        expected_value = expected.get(k.string())
        expected_value(v)

def test_hash_literals():
    inp = '''
        let two = "two";
        {
            "one": 10-9,
            two: 1+1,
            "thr" + "ee": 6/2,
            4: 4,
            true: 5,
            false: 6
        }
    '''
    evaluated = test_eval(inp)
    expected = {
                    MonkeyObjectString(value='one').hash_key(): 1,
                    MonkeyObjectString(value='two').hash_key(): 2,
                    MonkeyObjectString(value='three').hash_key(): 3,
                    MonkeyObjectInteger(value=4).hash_key(): 4,
                    MonkeyEvaluator.TRUE.hash_key(): 5,
                    MonkeyEvaluator.FALSE.hash_key(): 6,
                }
    if len(evaluated.pairs) != len(expected):
        print('hash has wrong num of pairs, got %s' %(len(evaluated.pairs)))
    #
    pairs = evaluated.pairs
    for expected_key in expected.keys():
        expected_value = expected.get(expected_key)
        pair_key_value = None
        pair_key = None
        for x in pairs.keys():
            if expected_key == x:
                pair_key = x
                pair_value = pairs.get(x)
                break
        #
        if expected_key != pair_key or \
            expected_value != pair_value.value.value:
            print('error: key %s expected %s, got %s' %(
                pair_key,
                expected_value, 
                pair_value.value.value))

def test_hash_index_expressions():
    tests = [
                [
                    '{"foo": 5}["foo"]',
                    5,
                ],
                [
                    '{"foo": 5}["bar"]',
                    None,
                ],
                [
                    'let key="foo"; {"foo": 5}[key]',
                    5,
                ],
                [
                    '{}["foo"]',
                    None,
                ],
                [
                    '{5: 5}[5]',
                    5,
                ],
                [
                    '{true: 5}[true]',
                    5,
                ],
                [
                    '{false: 5}[false]',
                    5,
                ],
        ]
    for t in tests:
        inp = t[0]
        evaluated = test_eval(inp)
        expected = t[1]
        if expected:
            test_integer_object(evaluated, expected)
        else:
            test_null_object(evaluated)

def main():
    test_next_token_1()
    test_next_token_2()
    test_let_statements()
    test_return_statements()
    test_string()
    test_identifier_expression()
    test_integer_literal_expression()
    test_parsing_prefix_expressions()
    test_parsing_infix_expressions()
    test_operator_precedence_parsing()
    test_boolean_literal_expression()
    test_if_expression()
    test_if_else_expression()
    test_function_literal_parsing()
    test_function_parameter_parsing()
    test_call_expression_parsing()
    test_call_expression_parameter_parsing()
    test_lets_statements_expression()
    test_eval_integer_expression()
    test_eval_boolean_expression()
    test_bang_operator()
    test_if_else_expressions()
    test_return_statements_eval()
    test_error_handling()
    test_let_statements_eval()
    test_function_object()
    test_function_application()
    test_closures()
    test_string_literal_expression()
    test_string_literal()
    test_string_concatenation()
    test_builtin_functions()
    test_parsing_array_literals()
    test_parsing_index_expressions()
    test_array_literals()
    test_array_index_expressions()
    test_parsing_hash_literal_string_keys()
    test_parsing_empty_hash_literal()
    test_parsing_hash_literals_with_expressions()
    test_hash_literals()
    test_hash_index_expressions()

if __name__ == '__main__':
    main()

