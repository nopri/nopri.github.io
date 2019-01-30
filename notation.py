#
# simple prefix/postfix notation evaluator
# (c) Noprianto <nop@noprianto.com>
# 2014
# License: LGPL
# Version: 0.01
# Website: https://github.com/nopri/notation
#
'''
simple prefix/postfix notation evaluator


Using helper functions
----------------------
>>> import notation
>>> notation.simple_prefix_notation('+ 1 2')
3.0
>>> notation.simple_prefix_notation('* + 1 2 3')
9.0
>>> notation.simple_prefix_notation('- * + 1 2 3 4')
5.0
>>> notation.simple_prefix_notation('** - * + 1 2 3 4 5')
3125.0
>>> notation.simple_prefix_notation('/ ** - * + 1 2 3 4 5 6')
520.8333333333334
>>> 

>>> notation.simple_postfix_notation('1 2 +')
3.0
>>> notation.simple_postfix_notation('1 2 + 3 *')
9.0
>>> notation.simple_postfix_notation('1 2 + 3 * 4 -')
5.0
>>> notation.simple_postfix_notation('1 2 + 3 * 4 - 5 **')
3125.0
>>> notation.simple_postfix_notation('1 2 + 3 * 4 - 5 ** 6 /')
520.8333333333334
>>> 


Inherit from SimplePrefixPostfixNotation
----------------------------------------
>>> import operator
>>> from notation import SimplePrefixPostfixNotation
>>> 
>>> class LimitedPrefixPostfixNotation(SimplePrefixPostfixNotation):
...     def __init__(self, reverse=False):
...         self.OPERATORS = {'+': operator.add}
...         self.reverse = reverse
... 
>>> 
>>> o = LimitedPrefixPostfixNotation()
>>> print o.evaluate('+ 1 2')
3.0
>>> print o.evaluate('* + 1 2 3')
None
>>> 

>>> class AnotherPrefixPostfixNotation(SimplePrefixPostfixNotation):
...     def __init__(self, reverse=False):
...         SimplePrefixPostfixNotation.__init__(self, reverse)
...         self.OPERATORS.pop('*')
...         self.OPERATORS['x'] = operator.mul
... 
>>> 
>>> o = AnotherPrefixPostfixNotation()
>>> print o.evaluate('+ 1 2')
3.0
>>> print o.evaluate('* + 1 2 3')
None
>>> print o.evaluate('x + 1 2 3')
9.0
>>> 
'''

import operator

__version__ = '0.01'


class SimplePrefixPostfixNotation:
    def __init__(self, reverse=False):
        self.OPERATORS = {
                          '+': operator.add,
                          '-': operator.sub,
                          '/': operator.truediv,
                          '*': operator.mul,
                          '%': operator.mod,
                          '**': operator.pow,
                          }
        self.reverse = reverse
        
    def evaluate0(self, expression): 
        stack = []
        
        e = str(expression).split()
        if not self.reverse:
            e = e[-1::-1]
        
        for i in e:
            if i not in self.OPERATORS.keys():
                n = float(i)    # ValueError
                if not self.reverse:
                    stack.append(n)
                else:
                    stack.insert(0, n)
            else:                
                o1 = stack.pop() #IndexError
                o2 = stack.pop() #IndexError
                res = self.OPERATORS.get(i)(o1, o2)
                if not self.reverse:
                    stack.append(res)    
                else:
                    stack.insert(0, res)
           
        return stack
    
    def evaluate(self, expression):
        res = None
        try:
            res = self.evaluate0(expression)
            if not len(res) == 1:
                raise Exception
            res = res[0]
        except:
            pass
        return res
    
    
def simple_prefix_notation(expression):
    o = SimplePrefixPostfixNotation()
    return o.evaluate(expression)


def simple_postfix_notation(expression):
    o = SimplePrefixPostfixNotation(reverse=True)
    return o.evaluate(expression)

