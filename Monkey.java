/*
Simple implementation of The Monkey Programming Language
interpreter in Python
Monkey.java
(c) Noprianto <nopri.anto@icloud.com>, 2019
Website: nopri.github.io
License: MIT
Version: 0.2

Minimum Java version: 5.0

Based on monkey.py
(c) Noprianto <nopri.anto@icloud.com>, 2019
monkey.py is based on code (in Go programming language) in book:
WRITING AN INTERPRETER IN GO

How to compile Monkey.java:
javac Monkey.java
    or
Use precompiled Monkey.jar (please download it from my website)

How to use Monkey.java:
- Standalone
  - No command line argument: interactive
        Monkey.java 0.2
        Press ENTER to quit
        >> let hello = "Hello World"
        >> hello
        "Hello World"
        >> 
  - Command line argument: try to interpret as file
        java Monkey test.monkey 
        or
        java -jar Monkey.jar test.monkey
    If exception occurred: interpret the argument as monkey code
        java Monkey "puts(1,2,3)"
        or
        java -jar Monkey.jar "puts(1,2,3)"

        1
        2
        3
        null
- Library
  Please see the example below

In Monkey.java, it is possible to set initial environment
when the interpreter is started. This allows integration
with external applications. For example:
code:

    import java.io.ByteArrayOutputStream;
    import java.io.PrintStream;
    import java.util.HashMap;
    import java.util.Map;

    public class External {
        public static void main(String[] args) {
            String result = "";

            Map<String, Object> map = new HashMap<String, Object>();
            map.put("hello", "Hello, World");
            map.put("test", true);

            MonkeyEnvironment env = MonkeyEnvironment.fromMap(map);

            ByteArrayOutputStream outputStream = new ByteArrayOutputStream();
            try {
                PrintStream output = new PrintStream(outputStream);
                Monkey.evaluatorString("puts(hello); puts(test); ERROR;", env, output);
                result = outputStream.toString();
            } catch (Exception e) {
            }

            System.out.println(result);
        }
    }

output:

    Hello, World
    true
    ERROR: identifier not found: ERROR

*/

import java.io.File;
import java.io.PrintStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

class MonkeyToken {
    static final String ILLEGAL = "ILLEGAL";
    static final String EOF = "EOF";
    static final String IDENT = "IDENT";
    static final String INT = "INT";
    static final String ASSIGN = "=";
    static final String PLUS = "+";
    static final String MINUS = "-";
    static final String BANG = "!";
    static final String ASTERISK = "*";
    static final String SLASH = "/";
    static final String LT = "<";
    static final String GT = ">";
    static final String COMMA = ",";
    static final String SEMICOLON = ";";
    static final String LPAREN = "(";
    static final String RPAREN = ")";
    static final String LBRACE = "{";
    static final String RBRACE = "}";
    static final String FUNCTION = "FUNCTION";
    static final String LET = "LET";
    static final String TRUE = "true";
    static final String FALSE = "false";
    static final String IF = "if";
    static final String ELSE = "else";
    static final String RETURN = "return";
    static final String EQ = "==";
    static final String NOT_EQ = "!=";
    static final String STRING = "STRING";
    static final String LBRACKET = "[";
    static final String RBRACKET = "]";
    static final String COLON = ":";

    private String type = "";
    private String literal = "";
    
    public MonkeyToken() {
    }

    public MonkeyToken(String type, String literal) {
        this.type = type;
        this.literal = literal;
    }
    
    public String getType() {
        return type;
    }
    
    public String getLiteral() {
        return literal;
    }
    
    public void setType(String type) {
        this.type = type;
    }
    
    public void setLiteral(String literal) {
        this.literal = literal;
    }
}

class MonkeyLexer {
    static final Map<String, String> KEYWORDS;
    static final String VALID_IDENTS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_";
    static final String VALID_NUMBERS = "0123456789";
    static final String WHITESPACES = " \t\r\n";
    static {
        KEYWORDS = new HashMap<String, String>();
        KEYWORDS.put("fn", MonkeyToken.FUNCTION);
        KEYWORDS.put("let", MonkeyToken.LET);
        KEYWORDS.put("true", MonkeyToken.TRUE);
        KEYWORDS.put("false", MonkeyToken.FALSE);
        KEYWORDS.put("if", MonkeyToken.IF);
        KEYWORDS.put("else", MonkeyToken.ELSE);
        KEYWORDS.put("return", MonkeyToken.RETURN);
    }
    
    private String input = "";
    private int position = 0;
    private int read = 0;
    private char ch = 0;

    public MonkeyLexer() {
    }
    
    public MonkeyLexer(String input, int position, int read, char ch) {
        this.input = input;
        this.position = position;
        this.read = read;
        this.ch = ch;
    }

    void readChar() {
        if (read >= input.length()) {
            ch = 0;
        } else {
            ch = input.charAt(read);
        }
        position = read;
        read += 1;
    }
    
    char peekChar() {
        if (read >= input.length()) {
            return 0;
        } else {
            return input.charAt(read);
        }
    }
    
    MonkeyToken newToken(MonkeyToken token, String type, char ch) {
        token.setType(type);
        token.setLiteral(String.valueOf(ch));
        return token;
    }
    
    MonkeyToken newToken(MonkeyToken token, String type, String ch) {
        token.setType(type);
        token.setLiteral(ch);
        return token;
    }

    MonkeyToken nextToken() {
        MonkeyToken t = new MonkeyToken();
        
        this.skipWhitespace();
        
        if (ch == '=') {
            if (peekChar() == '=') {
                String c = String.valueOf(ch);
                readChar();
                t = newToken(t, MonkeyToken.EQ, c + String.valueOf(ch));
            } else {
                t = newToken(t, MonkeyToken.ASSIGN, ch);
            }
        } else if (ch == '+') {
            t = newToken(t, MonkeyToken.PLUS, ch);
        } else if (ch == '-') {
            t = newToken(t, MonkeyToken.MINUS, ch);          
        } else if (ch == '!') {
            if (peekChar() == '=') {
                String c = String.valueOf(ch);
                readChar();
                t = newToken(t, MonkeyToken.NOT_EQ, c + String.valueOf(ch));
            } else {
                t = newToken(t, MonkeyToken.BANG, ch);
            }
        } else if (ch == '/') {
            t = newToken(t, MonkeyToken.SLASH, ch);     
        } else if (ch == '*') {
            t = newToken(t, MonkeyToken.ASTERISK, ch);      
        } else if (ch == '<') {
            t = newToken(t, MonkeyToken.LT, ch);      
        } else if (ch == '>') {
            t = newToken(t, MonkeyToken.GT, ch);      
        } else if (ch == ';') {
            t = newToken(t, MonkeyToken.SEMICOLON, ch);      
        } else if (ch == '(') {
            t = newToken(t, MonkeyToken.LPAREN, ch);      
        } else if (ch == ')') {
            t = newToken(t, MonkeyToken.RPAREN, ch);      
        } else if (ch == ',') {
            t = newToken(t, MonkeyToken.COMMA, ch);      
        } else if (ch == '+') {
            t = newToken(t, MonkeyToken.PLUS, ch);      
        } else if (ch == '{') {
            t = newToken(t, MonkeyToken.LBRACE, ch);      
        } else if (ch == '}') {
            t = newToken(t, MonkeyToken.RBRACE, ch);      
        } else if (ch == 0) {
            t.setLiteral("");
            t.setType(MonkeyToken.EOF);
        } else if (ch == '"') {
            t.setLiteral(readString());
            t.setType(MonkeyToken.STRING);
        } else if (ch == '[') {
            t = newToken(t, MonkeyToken.LBRACKET, ch);      
        } else if (ch == ']') {
            t = newToken(t, MonkeyToken.RBRACKET, ch);      
        } else if (ch == ':') {
            t = newToken(t, MonkeyToken.COLON, ch);      
        } else {
            if (isLetter(ch)) {
                t.setLiteral(readIdent());
                t.setType(lookUpIdent(t.getLiteral()));
                return t;
            } else if (isDigit(ch)) {
                t.setLiteral(readNumber());
                t.setType(MonkeyToken.INT);
                return t;
            } else {
                t = newToken(t, MonkeyToken.ILLEGAL, ch);      
            }
        }
        readChar();
        return t;
    }
    
    String readIdent() {
        int pos = position;
        while (true) {
            if (ch == 0) {
                break;
            }
            boolean test = isLetter(ch);
            if (!test) {
                break;
            }
            readChar();
        }
        String ret = input.substring(pos, position);
        return ret;
    }
    
    String readNumber() {
        int pos = position;
        while (true) {
            if (ch == 0) {
                break;
            }
            boolean test = isDigit(ch);
            if (!test) {
                break;
            }
            readChar();
        }
        String ret = input.substring(pos, position);
        return ret;
    }
    
    String readString() {
        int pos = position + 1;
        while (true) {
            readChar();
            if (ch == '"' || ch == 0) {
                break;
            }
        }
        String ret = input.substring(pos, position);
        return ret;
    }
    
    String lookUpIdent(String s) {
        String ret = KEYWORDS.get(s);
        if (ret != null) {
            return ret;
        }
        return MonkeyToken.IDENT;
    }
    
    boolean isLetter(char c) {
        return VALID_IDENTS.indexOf(c) > -1;
    }
    
    boolean isDigit(char c) {
        return VALID_NUMBERS.indexOf(c) > -1;
    }
    
    void skipWhitespace() {
        while (WHITESPACES.indexOf(ch) > -1) {
            readChar();
        }
    }
    
    void setInput(String input) {
        this.input = input;
    }
    
    public static MonkeyLexer newInstance(String s) {
        MonkeyLexer l = new MonkeyLexer();
        l.setInput(s);
        l.readChar();
        return l;
    }
}

class MonkeyNode {
    protected MonkeyToken token;
    
    public MonkeyNode() {
    }
    
    public void setToken(MonkeyToken token) {
        this.token = token;
    }
    
    public String tokenLiteral() {
        return token.getLiteral();
    }
    
    @Override
    public String toString() {
        return "";
    }
}

class MonkeyStatement extends MonkeyNode {
    public MonkeyStatement() {
    }
    
    public void statementNode() {
    }    
}

class MonkeyExpression extends MonkeyNode {
    public MonkeyExpression() {
    }
    
    public void expressionNode() {
    }    
}

class MonkeyIdentifier extends MonkeyExpression {
    private String value = "";
    
    public MonkeyIdentifier(String value) {
        this.value = value;
        this.token = new MonkeyToken();
    }
    
    public String getValue() {
        return value;
    }
    
    public void setValue(String value) {
        this.value = value;
    }
    
    @Override
    public String toString() {
        return value;
    }
}

class MonkeyLetStatement extends MonkeyStatement {
    private MonkeyIdentifier name;
    private MonkeyExpression value;
    
    public MonkeyLetStatement() {
        this.token = new MonkeyToken();
        this.name = new MonkeyIdentifier("");
        this.value = new MonkeyExpression();
    }
    
    public MonkeyExpression getValue() {
        return value;
    }
    
    public MonkeyIdentifier getName() {
        return name;
    }
    
    public void setName(MonkeyIdentifier name) {
        this.name = name;
    }
    
    public void setValue(MonkeyExpression value) {
        this.value = value;
    }
    
    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        ret.append(tokenLiteral());
        ret.append(" ");
        ret.append(name);
        ret.append(" = ");
        //
        if (value != null) {
            ret.append(value);
        }
        //
        ret.append(";");
        return ret.toString();
    }
}

class MonkeyReturnStatement extends MonkeyStatement {
    private MonkeyExpression returnValue;

    public MonkeyReturnStatement() {
        this.token = new MonkeyToken();
        this.returnValue = new MonkeyExpression();
    }
    
    public MonkeyExpression getReturnValue() {
        return returnValue;
    }
    
    public void setReturnValue(MonkeyExpression returnValue) {
        this.returnValue = returnValue;
    }
    
    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        ret.append(tokenLiteral());
        ret.append(" ");
        if (returnValue != null) {
            ret.append(returnValue);
        }
        ret.append(";");
        return ret.toString();
    }
    
}

class MonkeyExpressionStatement extends MonkeyStatement {
    private MonkeyExpression expression;

    public MonkeyExpressionStatement() {
        this.token = new MonkeyToken();
        this.expression = new MonkeyExpression();
    }
    
    public MonkeyExpression getExpression() {
        return expression;
    }
    
    public void setExpression(MonkeyExpression expression) {
        this.expression = expression;
    }
    
    @Override
    public String toString() {
        if (expression != null) {
            return expression.toString();
        }
        return "";
    }
}

class MonkeyBlockStatement extends MonkeyStatement {
    private List<MonkeyStatement> statements;

    public MonkeyBlockStatement() {
        this.token = new MonkeyToken();
        this.statements = new ArrayList<MonkeyStatement>();
    }
    
    public List<MonkeyStatement> getStatements() {
        return statements;
    }
    
    public boolean isEmpty() {
        return statements.isEmpty();
    }
    
    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        ret.append(String.format("%s{%s", Monkey.LINESEP, Monkey.LINESEP));
        //
        for(MonkeyStatement s: statements) {
            ret.append(String.format("%s;%s", s.toString(), Monkey.LINESEP));
        }
        //
        ret.append(String.format("}%s", Monkey.LINESEP));
        return ret.toString();
    }
}

class MonkeyIntegerLiteral extends MonkeyExpression {
    private int value;

    public MonkeyIntegerLiteral(int value) {
        this.token = new MonkeyToken();
        this.value = value;
    }
    
    public int getValue() {
        return value;
    }
    
    @Override
    public String toString() {
        return token.getLiteral();
    }
    
}

class MonkeyStringLiteral extends MonkeyExpression {
    private String value;

    public MonkeyStringLiteral() {
        this.token = new MonkeyToken();
        this.value = "";    
    }
    
    public MonkeyStringLiteral(String value) {
        this.token = new MonkeyToken();
        this.value = value;
    }
    
    public String getValue() {
        return value;
    }

    @Override
    public String toString() {
        return token.getLiteral();
    }
}

class MonkeyFunctionLiteral extends MonkeyExpression {
    private List<MonkeyIdentifier> parameters;
    private MonkeyBlockStatement body;

    public MonkeyFunctionLiteral() {
        this.token = new MonkeyToken();
        this.parameters = new ArrayList<MonkeyIdentifier>();
        this.body = new MonkeyBlockStatement();
    }
    
    public List<MonkeyIdentifier> getParameters() {
        return parameters;
    }
    
    public MonkeyBlockStatement getBody() {
        return body;
    }
    
    public void setParameters(List<MonkeyIdentifier> parameters) {
        this.parameters = parameters;
    }
    
    public void setBody(MonkeyBlockStatement body) {
        this.body = body;
    }
    
    @Override
    public String toString() {
        List<String> params = new ArrayList<String>();
        for (MonkeyIdentifier p: parameters) {
            params.add(p.toString());
        }
        //
        StringBuilder ret = new StringBuilder();
        ret.append(tokenLiteral());
        ret.append("(");
        ret.append(MonkeyUtil.stringJoin(", ", params));
        ret.append(")");
        ret.append(body.toString());
        //
        return ret.toString();
    }
}

class MonkeyCallExpression extends MonkeyExpression {
    private MonkeyExpression function;
    private List<MonkeyExpression> arguments;

    public MonkeyCallExpression() {
        this.token = new MonkeyToken();
        this.function = new MonkeyExpression();
        this.arguments = new ArrayList<MonkeyExpression>();
    }
    
    public MonkeyExpression getFunction() {
        return function;
    }
    
    public List<MonkeyExpression> getArguments() {
        return arguments;
    }
    
    public void setFunction(MonkeyExpression function) {
        this.function = function;
    }
    
    public void setArguments(List<MonkeyExpression> arguments) {
        this.arguments = arguments;
    }
    
    @Override
    public String toString() {
        List<String> args = new ArrayList<String>();
        for (MonkeyExpression a: arguments) {
            args.add(a.toString());
        }
        //
        StringBuilder ret = new StringBuilder();
        ret.append(function.toString());
        ret.append("(");
        ret.append(MonkeyUtil.stringJoin(", ", args));
        ret.append(")");
        //
        return ret.toString();
    }
}

class MonkeyBoolean extends MonkeyExpression {
    private boolean value;

    public MonkeyBoolean(boolean value) {
        this.token = new MonkeyToken();
        this.value = value;
    }
    
    public boolean getValue() {
        return value;
    }
    
    @Override
    public String toString() {
        return token.getLiteral();
    }
}

class MonkeyPrefixExpression extends MonkeyExpression {
    private String operator;
    private MonkeyExpression right;

    public MonkeyPrefixExpression() {
        this.token = new MonkeyToken();
        this.operator = "";
        this.right = new MonkeyExpression();
    }
    
    public void setOperator(String operator) {
        this.operator = operator;
    }

    public MonkeyExpression getRight() {
        return right;
    }
    
    public String getOperator() {
        return operator;
    }
    
    public void setRight(MonkeyExpression right) {
        this.right = right;
    }
    
    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        ret.append("(");
        ret.append(operator);
        ret.append(right.toString());
        ret.append(")");
        //
        return ret.toString();
    }
}

class MonkeyInfixExpression extends MonkeyExpression {
    private MonkeyExpression left;
    private String operator;
    private MonkeyExpression right;

    public MonkeyInfixExpression() {
        this.token = new MonkeyToken();
        this.left = new MonkeyExpression();
        this.operator = "";
        this.right = new MonkeyExpression();
    }
    
    public MonkeyExpression getLeft() {
        return left;
    }
    
    public MonkeyExpression getRight() {
        return right;
    }
    
    public String getOperator() {
        return operator;
    }
    
    public void setOperator(String operator) {
        this.operator = operator;
    }
    
    public void setLeft(MonkeyExpression left) {
        this.left = left;
    }
    
    public void setRight(MonkeyExpression right) {
        this.right = right;
    }
    
    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        ret.append("(");
        ret.append(left.toString());
        ret.append(" ");
        ret.append(operator);
        ret.append(" ");
        ret.append(right.toString());
        ret.append(")");
        //
        return ret.toString();
    }
}

class MonkeyIfExpression extends MonkeyExpression {
    private MonkeyExpression condition;
    private MonkeyBlockStatement consequence;
    private MonkeyBlockStatement alternative;

    public MonkeyIfExpression() {
        this.token = new MonkeyToken();
        this.condition = new MonkeyExpression();
        this.consequence = new MonkeyBlockStatement();
        this.alternative = new MonkeyBlockStatement();
    }
    
    public void setCondition(MonkeyExpression condition) {
        this.condition = condition;
    }
    
    public void setConsequence(MonkeyBlockStatement consequence) {
        this.consequence = consequence;
    }
    
    public void setAlternative(MonkeyBlockStatement alternative) {
        this.alternative = alternative;
    }
    
    public MonkeyExpression getCondition() {
        return condition;
    }
    
    public MonkeyBlockStatement getConsequence() {
        return consequence;
    }
    
    public MonkeyBlockStatement getAlternative() {
        return alternative;
    }
    
    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        ret.append("if");
        ret.append(condition.toString());
        ret.append(" ");
        ret.append(consequence.toString());
        //
        if (!alternative.isEmpty()) {
            ret.append(" else ");
            ret.append(alternative.toString());
        }
        //
        return ret.toString();
    }
}

class MonkeyArrayLiteral extends MonkeyExpression {
    private List<MonkeyExpression> elements;

    public MonkeyArrayLiteral() {
        this.token = new MonkeyToken();
        this.elements = new ArrayList<MonkeyExpression>();
    }
    
    public List<MonkeyExpression> getElements() {
        return elements;
    }
    
    public void setElements(List<MonkeyExpression> elements) {
        this.elements = elements;
    }

    @Override
    public String toString() {
        List<String> elements = new ArrayList<String>();
        for (MonkeyExpression e: this.elements) {
            elements.add(e.toString());
        }
        //
        StringBuilder ret = new StringBuilder();
        ret.append("[");
        ret.append(MonkeyUtil.stringJoin(", ", elements));
        ret.append("]");
        //
        return ret.toString();
    }
}

class MonkeyIndexExpression extends MonkeyExpression {
    private MonkeyExpression left;
    private MonkeyExpression index;

    public MonkeyIndexExpression() {
        this.token = new MonkeyToken();
        this.left = new MonkeyExpression();
        this.index = new MonkeyExpression();
    }
    
    public MonkeyExpression getLeft() {
        return left;
    }
    
    public MonkeyExpression getIndex() {
        return index;
    }
    
    public void setLeft(MonkeyExpression left) {
        this.left = left;
    }
    
    public void setIndex(MonkeyExpression index) {
        this.index = index;
    }
    
    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        ret.append("(");
        ret.append(left.toString());
        ret.append("[");
        ret.append(index.toString());
        ret.append("])");
        //
        return ret.toString();
    }
}

class MonkeyHashLiteral extends MonkeyExpression {
    private Map<MonkeyExpression, MonkeyExpression> pairs;

    public MonkeyHashLiteral() {
        this.token = new MonkeyToken();
        this.pairs = new HashMap<MonkeyExpression, MonkeyExpression>();
    }   
    
    public void setPairs(Map<MonkeyExpression, MonkeyExpression> pairs) {
        this.pairs = pairs;
    }
    
    public Map<MonkeyExpression, MonkeyExpression> getPairs() {
        return pairs;
    }
    
    @Override
    public String toString() {
        List<String> pairs = new ArrayList<String>();
        for (MonkeyExpression k: this.pairs.keySet()) {
            MonkeyExpression v = this.pairs.get(k);
            pairs.add(String.format("%s:%s", k.toString(), v.toString()));
        }
        //
        StringBuilder ret = new StringBuilder();
        ret.append("{");
        ret.append(MonkeyUtil.stringJoin(", ", pairs));
        ret.append("}");
        //
        return ret.toString();
    }
}

class MonkeyParser {
    public static final int LOWEST = 1;
    public static final int EQUALS = 2;
    public static final int LESSGREATER = 3;
    public static final int SUM = 4;
    public static final int PRODUCT = 5;
    public static final int PREFIX = 6;
    public static final int CALL = 7;
    public static final int INDEX = 8;
    
    public static final Map<String, Integer> PRECEDENCES;
    static {
        PRECEDENCES = new HashMap<String, Integer>();
        PRECEDENCES.put(MonkeyToken.LPAREN, CALL);
        PRECEDENCES.put(MonkeyToken.EQ, EQUALS);
        PRECEDENCES.put(MonkeyToken.NOT_EQ, EQUALS);
        PRECEDENCES.put(MonkeyToken.LT, LESSGREATER);
        PRECEDENCES.put(MonkeyToken.GT, LESSGREATER);
        PRECEDENCES.put(MonkeyToken.PLUS, SUM);
        PRECEDENCES.put(MonkeyToken.MINUS, SUM);
        PRECEDENCES.put(MonkeyToken.SLASH, PRODUCT);
        PRECEDENCES.put(MonkeyToken.ASTERISK, PRODUCT);
        PRECEDENCES.put(MonkeyToken.LBRACKET, INDEX);
    }
    
    private MonkeyLexer lexer;
    private MonkeyToken curToken;
    private MonkeyToken peekToken;
    private List<String> errors;
    private Map<String, MonkeyParserPrefixCallable> prefixParseFns;
    private Map<String, MonkeyParserInfixCallable> infixParseFns;

    class ParseIdentifer implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            MonkeyIdentifier ret = new MonkeyIdentifier("");
            ret.setToken(curToken);
            ret.setValue(curToken.getLiteral());
            return ret;
        }        
    }

    class ParseIntegerLiteral implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            int test;
            try {
                test = Integer.parseInt(curToken.getLiteral());
            } catch (NumberFormatException e) {
                String msg = String.format("could not parse %s as integer", curToken.getLiteral());
                errors.add(msg);
                return null;
            }
            MonkeyIntegerLiteral lit = new MonkeyIntegerLiteral(test);
            lit.setToken(curToken);
            return lit;
        }        
    }
    
    class ParsePrefixExpression implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            MonkeyPrefixExpression e = new MonkeyPrefixExpression();
            e.setToken(curToken);
            e.setOperator(curToken.getLiteral());
            //
            nextToken();
            e.setRight(parseExpression(PREFIX));
            //
            return e;            
        }        
    }
    
    class ParseBoolean implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            MonkeyBoolean ret = new MonkeyBoolean(curTokenIs(MonkeyToken.TRUE));
            ret.setToken(curToken);
            return ret;            
        }        
    }

    class ParseGroupedExpression implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            nextToken();
            MonkeyExpression e = parseExpression(LOWEST);
            //
            if (!expectPeek(MonkeyToken.RPAREN)) {
                return null;
            }
            //
            return e;
        }        
    }

    class ParseIfExpression implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            MonkeyIfExpression e = new MonkeyIfExpression();
            e.setToken(curToken);
            //
            if (!expectPeek(MonkeyToken.LPAREN)) {
                return null;
            }
            //
            nextToken();
            e.setCondition(parseExpression(LOWEST));
            //
            if (!expectPeek(MonkeyToken.RPAREN)) {
                return null;
            }
            //
            if (!expectPeek(MonkeyToken.LBRACE)) {
                return null;
            }
            //
            e.setConsequence(parseBlockStatement());
            //
            if (peekTokenIs(MonkeyToken.ELSE)) {
                nextToken();
                //
                if (!expectPeek(MonkeyToken.LBRACE)) {
                    return null;
                }
                e.setAlternative(parseBlockStatement());
                
            }
            //
            return e;
        }        
    }
    
    class ParseFunctionLiteral implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            MonkeyFunctionLiteral lit = new MonkeyFunctionLiteral();
            lit.setToken(curToken);
            //
            if (!expectPeek(MonkeyToken.LPAREN)) {
                return null;
            }
            //
            lit.setParameters(parseFunctionParameters());
            //
            if (!expectPeek(MonkeyToken.LBRACE)) {
                return null;
            }
            //
            lit.setBody(parseBlockStatement());
            //
            return lit;
        }
    }

    class ParseStringLiteral implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            MonkeyStringLiteral lit = new MonkeyStringLiteral(curToken.getLiteral());
            lit.setToken(curToken);        
            return lit;
        }        
    }
    
    class ParseArrayLiteral implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            MonkeyArrayLiteral array = new MonkeyArrayLiteral();
            array.setToken(curToken);
            array.setElements(parseExpressionList(MonkeyToken.RBRACKET));
            return array;
        }        
    }
    
    class ParseHashLiteral implements MonkeyParserPrefixCallable {
        public MonkeyExpression call() {
            MonkeyHashLiteral h = new MonkeyHashLiteral();
            h.setToken(curToken);
            //
            while (!peekTokenIs(MonkeyToken.RBRACE)) {
                nextToken();
                MonkeyExpression key = parseExpression(LOWEST);
                //
                if (!expectPeek(MonkeyToken.COLON)) {
                    return null;
                }
                //
                nextToken();
                MonkeyExpression value = parseExpression(LOWEST);
                //
                h.getPairs().put(key, value);
                //
                if (!peekTokenIs(MonkeyToken.RBRACE) && !expectPeek(MonkeyToken.COMMA)) {
                    return null;
                }
            }
            if (!expectPeek(MonkeyToken.RBRACE)) {
                return null;
            }
            //
            return h;
        }        
    }

    class ParseInfixExpression implements MonkeyParserInfixCallable {
        public MonkeyExpression call(MonkeyExpression expression) {
            MonkeyInfixExpression e = new MonkeyInfixExpression();
            e.setToken(curToken);
            e.setOperator(curToken.getLiteral());
            e.setLeft(expression);
            //
            int precedence = curPrecedence();
            nextToken();
            //
            e.setRight(parseExpression(precedence));
            //
            return e;
        }
    }

    class ParseCallExpression implements MonkeyParserInfixCallable {
        public MonkeyExpression call(MonkeyExpression expression) {
            MonkeyCallExpression exp = new MonkeyCallExpression();
            exp.setToken(curToken);
            exp.setFunction(expression);
            exp.setArguments(parseExpressionList(MonkeyToken.RPAREN));
            return exp;
        }
    }

    class ParseIndexExpression implements MonkeyParserInfixCallable {
        public MonkeyExpression call(MonkeyExpression expression) {
            MonkeyIndexExpression exp = new MonkeyIndexExpression();
            exp.setToken(curToken);
            exp.setLeft(expression);
            //
            nextToken();
            exp.setIndex(parseExpression(LOWEST));
            //
            if (!expectPeek(MonkeyToken.RBRACKET)) {
                return null;
            }
            //
            return exp;
        }
    }
    
    public MonkeyParser() {
        this.lexer = MonkeyLexer.newInstance("");
        this.curToken = new MonkeyToken();
        this.peekToken = new MonkeyToken();
        this.errors = new ArrayList<String>();
        this.prefixParseFns = new HashMap<String, MonkeyParserPrefixCallable>();
        this.infixParseFns = new HashMap<String, MonkeyParserInfixCallable>();
        //
        registerPrefix(MonkeyToken.IDENT, new ParseIdentifer());
        registerPrefix(MonkeyToken.INT, new ParseIntegerLiteral());
        registerPrefix(MonkeyToken.BANG, new ParsePrefixExpression());
        registerPrefix(MonkeyToken.MINUS, new ParsePrefixExpression());
        registerPrefix(MonkeyToken.TRUE, new ParseBoolean());
        registerPrefix(MonkeyToken.FALSE, new ParseBoolean());
        registerPrefix(MonkeyToken.LPAREN, new ParseGroupedExpression());
        registerPrefix(MonkeyToken.IF, new ParseIfExpression());
        registerPrefix(MonkeyToken.FUNCTION, new ParseFunctionLiteral());
        registerPrefix(MonkeyToken.STRING, new ParseStringLiteral());
        registerPrefix(MonkeyToken.LBRACKET, new ParseArrayLiteral());
        registerPrefix(MonkeyToken.LBRACE, new ParseHashLiteral());
        //
        registerInfix(MonkeyToken.PLUS, new ParseInfixExpression());
        registerInfix(MonkeyToken.MINUS, new ParseInfixExpression());
        registerInfix(MonkeyToken.SLASH, new ParseInfixExpression());
        registerInfix(MonkeyToken.ASTERISK, new ParseInfixExpression());
        registerInfix(MonkeyToken.EQ, new ParseInfixExpression());
        registerInfix(MonkeyToken.NOT_EQ, new ParseInfixExpression());
        registerInfix(MonkeyToken.LT, new ParseInfixExpression());
        registerInfix(MonkeyToken.GT, new ParseInfixExpression());
        registerInfix(MonkeyToken.LPAREN, new ParseCallExpression());
        registerInfix(MonkeyToken.LBRACKET, new ParseIndexExpression());
    }
    
    public List<String> getErrors() {
        return errors;
    }
    
    void nextToken() {
        curToken = peekToken;
        peekToken = lexer.nextToken();
    }

    MonkeyProgram parseProgram() {
        MonkeyProgram program = new MonkeyProgram();
        
        while (!curToken.getType().equals(MonkeyToken.EOF)) {
            MonkeyStatement s = parseStatement();
            if (s != null) {
                program.getStatements().add(s);
            }
            nextToken();
        }
        
        return program;
    }
    
    MonkeyStatement parseStatement() {
        if (curToken.getType().equals(MonkeyToken.LET)) {
            return parseLetStatement();
        } else if (curToken.getType().equals(MonkeyToken.RETURN)) {
            return parseReturnStatement();
        } else {
            return parseExpressionStatement();
        }
    }
    
    MonkeyLetStatement parseLetStatement() {
        MonkeyLetStatement s = new MonkeyLetStatement();
        s.setToken(curToken);
        if (!expectPeek(MonkeyToken.IDENT)) {
            return null;
        }
        //
        MonkeyIdentifier ident = new MonkeyIdentifier(curToken.getLiteral());
        ident.setToken(curToken);
        s.setName(ident);
        if (!expectPeek(MonkeyToken.ASSIGN)) {
            return null;
        }
        nextToken();
        s.setValue(parseExpression(LOWEST));
        if (peekTokenIs(MonkeyToken.SEMICOLON)) {
            nextToken();
        }
        //
        return s;
    }
    
    MonkeyReturnStatement parseReturnStatement() {
        MonkeyReturnStatement s = new MonkeyReturnStatement();
        s.setToken(curToken);
        
        nextToken();
        s.setReturnValue(parseExpression(LOWEST));
        if (peekTokenIs(MonkeyToken.SEMICOLON)) {
            nextToken();
        }
        //
        return s;
    }
    
    MonkeyExpressionStatement parseExpressionStatement() {
        MonkeyExpressionStatement s = new MonkeyExpressionStatement();
        s.setToken(curToken);
        s.setExpression(parseExpression(LOWEST));
        //
        if (peekTokenIs(MonkeyToken.SEMICOLON)) {
            nextToken();
        }
        //
        return s;
    }
    
    MonkeyBlockStatement parseBlockStatement() {
        MonkeyBlockStatement block = new MonkeyBlockStatement();
        block.setToken(curToken);
        //
        nextToken();
        while (!curTokenIs(MonkeyToken.RBRACE) && !curTokenIs(MonkeyToken.EOF)) {
            MonkeyStatement s = parseStatement();
            if (s != null) {
                block.getStatements().add(s);
            }
            nextToken();
        }
        //
        return block;
    }
    
    MonkeyExpression parseExpression(int precedence) {
        MonkeyParserPrefixCallable prefix = prefixParseFns.get(curToken.getType());
        if (prefix == null) {
            noPrefixParseFnError(curToken.getType());
            return null;
        }
        MonkeyExpression leftExp = prefix.call();
        //
        while (!peekTokenIs(MonkeyToken.SEMICOLON) && precedence < peekPrecedence()) {
            MonkeyParserInfixCallable infix = infixParseFns.get(peekToken.getType());
            if (infix == null) {
                return leftExp;
            }
            //
            nextToken();
            leftExp = infix.call(leftExp);
        }
        //
        return leftExp;       
    } 
    
    List<MonkeyIdentifier> parseFunctionParameters() {
        List<MonkeyIdentifier> identifiers = new ArrayList<MonkeyIdentifier>();
        //
        if (peekTokenIs(MonkeyToken.RPAREN)) {
            nextToken();
            return identifiers;
        }
        //
        nextToken();
        MonkeyIdentifier ident = new MonkeyIdentifier("");
        ident.setToken(curToken);
        ident.setValue(curToken.getLiteral());
        identifiers.add(ident);
        //
        while (peekTokenIs(MonkeyToken.COMMA)) {
            nextToken();
            nextToken();
            ident = new MonkeyIdentifier("");
            ident.setToken(curToken);
            ident.setValue(curToken.getLiteral());
            identifiers.add(ident);
        }
        //
        if (!expectPeek(MonkeyToken.RPAREN)) {
            return null;
        }
        //
        return identifiers;
    }

    List<MonkeyExpression> parseExpressionList(String end) {
        List<MonkeyExpression> ret = new ArrayList<MonkeyExpression>();
        //
        if (peekTokenIs(end)) {
            nextToken();
            return ret;
        }
        //
        nextToken();
        ret.add(parseExpression(LOWEST));
        //
        while (peekTokenIs(MonkeyToken.COMMA)) {
            nextToken();
            nextToken();
            ret.add(parseExpression(LOWEST));
        }
        //
        if (!expectPeek(end)) {
            return null;
        }
        //
        return ret;
    }
    
    boolean curTokenIs(String t) {
        return curToken.getType().equals(t);
    }
    
    boolean peekTokenIs(String t) {
        return peekToken.getType().equals(t);
    }
    
    boolean expectPeek(String t) {
        if (peekTokenIs(t)) {
            nextToken();
            return true;
        } else {
            peekError(t);
            return false;
        }
    }
    
    void peekError(String t) {
        String m = String.format("expected next token to be %s, got %s instead", t, peekToken.getType());
        errors.add(m);
    }
    
    void registerPrefix(String tokenType, MonkeyParserPrefixCallable fn) {
        prefixParseFns.put(tokenType, fn);
    }
    
    void registerInfix(String tokenType, MonkeyParserInfixCallable fn) {
        infixParseFns.put(tokenType, fn);
    }

    void noPrefixParseFnError(String tokenType) {
        String m = String.format("no prefix parse function for %s found", tokenType);
        errors.add(m);
    }
    
    int peekPrecedence() {
        Integer p = PRECEDENCES.get(peekToken.getType());
        if (p != null) {
            return p;
        }
        //
        return LOWEST;
    }


    int curPrecedence() {
        Integer p = PRECEDENCES.get(curToken.getType());
        if (p != null) {
            return p;
        }
        //
        return LOWEST;
    }
    
    public void setLexer(MonkeyLexer lexer) {
        this.lexer = lexer;
    }
    
    public static MonkeyParser newInstance(MonkeyLexer l) {
        MonkeyParser p = new MonkeyParser();
        p.setLexer(l);
        p.nextToken();
        p.nextToken();
        return p;
    }
}

interface MonkeyParserPrefixCallable {
    MonkeyExpression call();
}

interface MonkeyParserInfixCallable {
    MonkeyExpression call(MonkeyExpression expression);
}

class MonkeyProgram extends MonkeyNode {
    private List<MonkeyStatement> statements;

    public MonkeyProgram() {
        statements = new ArrayList<MonkeyStatement>();
    }
    
    List<MonkeyStatement> getStatements() {
        return statements;
    }
    
    @Override
    public String tokenLiteral() {
        if (statements.size() > 0) {
            return statements.get(0).tokenLiteral();
        } else {
            return "";
        }
    }

    @Override
    public String toString() {
        StringBuilder ret = new StringBuilder();
        for (MonkeyStatement s: statements) {
            ret.append(s.toString());
        }
        return ret.toString();
    }    
}

interface MonkeyHashable {
    MonkeyHashKey hashKey();
}

class MonkeyObject {
    public static final String INTEGER_OBJ = "INTEGER";
    public static final String BOOLEAN_OBJ = "BOOLEAN";
    public static final String NULL_OBJ = "NULL";
    public static final String RETURN_VALUE_OBJ = "RETURN_VALUE";
    public static final String ERROR_OBJ = "ERROR";
    public static final String FUNCTION_OBJ = "FUNCTION";
    public static final String STRING_OBJ = "STRING";
    public static final String BUILTIN_OBJ = "BUILTIN";
    public static final String ARRAY_OBJ = "ARRAY";
    public static final String HASH_OBJ = "HASH";
    
    protected String type;

    public MonkeyObject() {
        this.type = "";
    }
    
    public String getType() {
        return type;
    }
    
    public String inspect() {
        return "";
    }
    
    public String inspectValue() {
        return inspect();
    }
}

class MonkeyObjectInteger extends MonkeyObject implements MonkeyHashable {
    private int value;

    public MonkeyObjectInteger() {
        type = INTEGER_OBJ;
    }

    public MonkeyObjectInteger(int value) {
        this();
        this.value = value;
    }

    public int getValue() {
        return value;
    }
    
    public void setValue(int value) {
        this.value = value;
    }
    
    public MonkeyHashKey hashKey() {
        return new MonkeyHashKey(type, value);
    }

    @Override
    public String inspect() {
        return String.valueOf(value);
    }
}

class MonkeyObjectString extends MonkeyObject implements MonkeyHashable {
    private String value;

    public MonkeyObjectString() {
        type = STRING_OBJ;
    }

    public MonkeyObjectString(String value) {
        this();
        this.value = value;
    }
    
    public String getValue() {
        return value;
    }

    public void setValue(String value) {
        this.value = value;
    }
    
    @Override
    public String inspect() {
        return String.format("\"%s\"", value);
    }

    @Override
    public String inspectValue() {
        return value;
    }

    public MonkeyHashKey hashKey() {
        return new MonkeyHashKey(type, value.hashCode());
    }
    
}

class MonkeyObjectBoolean extends MonkeyObject implements MonkeyHashable {
    private boolean value;

    public MonkeyObjectBoolean() {
        type = BOOLEAN_OBJ;
    }

    public MonkeyObjectBoolean(boolean value) {
        this();
        this.value = value;
    }
    
    @Override
    public String inspect() {
        return String.format("%s", value);
    }

    public MonkeyHashKey hashKey() {
        int hashValue;
        if (value) {
            hashValue = 1;
        } else {
            hashValue = 0;
        }
        return new MonkeyHashKey(getType(), hashValue);
    }
}

class MonkeyObjectNull extends MonkeyObject {
    public MonkeyObjectNull() {
        type = NULL_OBJ;
    }

    @Override
    public String inspect() {
        return "null";
    }
}

class MonkeyObjectReturnValue extends MonkeyObject {
    private MonkeyObject value;

    public MonkeyObjectReturnValue() {
        type = RETURN_VALUE_OBJ;
    }
    
    public MonkeyObject getValue () {
        return value;
    }
    
    public void setValue(MonkeyObject value) {
        this.value = value;
    }
    
    @Override
    public String inspect() {
        return value.inspect();
    }
}

class MonkeyObjectError extends MonkeyObject {
    private String value;
    private String message;

    public MonkeyObjectError() {
        value = "";
        message = "";
        type = ERROR_OBJ;
    }

    public MonkeyObjectError(String value, String message) {
        this();
        this.value = value;
        this.message = message;
    }

    public void setMessage(String message) {
        this.message = message;
    }
    
    @Override
    public String inspect() {
        return String.format("ERROR: %s", message);
    }
}

class MonkeyObjectFunction extends MonkeyObject {
    private List<MonkeyIdentifier> parameters;
    private MonkeyBlockStatement body;
    private MonkeyEnvironment env;

    public MonkeyObjectFunction() {
        parameters = new ArrayList<MonkeyIdentifier>();
        body = new MonkeyBlockStatement();
        env = MonkeyEnvironment.newInstance();
    }

    public List<MonkeyIdentifier> getParameters() {
        return parameters;
    }
    
    public MonkeyBlockStatement getBody() {
        return body;
    }
    
    public MonkeyEnvironment getEnvironment() {
        return env;
    }
    
    public void setParameter(List<MonkeyIdentifier> parameters) {
        this.parameters = parameters;
    }
    
    public void setBody(MonkeyBlockStatement body) {
        this.body = body;
    }
    
    public void setEnvironment(MonkeyEnvironment env) {
        this.env = env;
    }
    
    @Override
    public String getType() {
        return FUNCTION_OBJ;
    }

    @Override
    public String inspect() {
        List<String> params = new ArrayList<String>();
        for (MonkeyIdentifier p: parameters) {
            params.add(p.toString());
        }
        //
        StringBuilder ret = new StringBuilder();
        ret.append("fn");
        ret.append("(");
        ret.append(MonkeyUtil.stringJoin(", ", params));
        ret.append(")");
        ret.append(body.toString());
        //
        return ret.toString();
    }
}

class MonkeyObjectBuiltin extends MonkeyObject {
    private MonkeyBuiltinCallable fn;
    private String value;

    public MonkeyObjectBuiltin(MonkeyBuiltinCallable fn, String value) {
        this.fn = fn;
        this.value = value;
    }

    public MonkeyObjectBuiltin(MonkeyBuiltinCallable fn) {
        this.fn = fn;
        this.value = "";
    }

    public MonkeyBuiltinCallable getFn() {
        return fn;
    }
    
    @Override
    public String getType() {
        return BUILTIN_OBJ;
    }

    @Override
    public String inspect() {
        return "builtin function";
    }
}

class MonkeyObjectArray extends MonkeyObject {
    private List<MonkeyObject> elements;

    public MonkeyObjectArray() {
        elements = new ArrayList<MonkeyObject>();
    }

    public List<MonkeyObject> getElements() {
        return elements;
    }
    
    public void setElements(List<MonkeyObject> elements) {
        this.elements = elements;
    }
    
    @Override
    public String getType() {
        return ARRAY_OBJ;
    }

    @Override
    public String inspect() {
        List<String> list = new ArrayList<String>();
        for (MonkeyObject e: elements) {
            list.add(e.inspect());
        }
        //
        StringBuilder ret = new StringBuilder();
        ret.append("[");
        ret.append(MonkeyUtil.stringJoin(", ", list));
        ret.append("]");
        //
        return ret.toString();
    }
}

class MonkeyObjectHash extends MonkeyObject {
    private Map<MonkeyHashKey, MonkeyHashPair> pairs;

    public MonkeyObjectHash() {
        pairs = new HashMap<MonkeyHashKey, MonkeyHashPair>();
    }
    
    public Map<MonkeyHashKey, MonkeyHashPair> getPairs() {
        return pairs;
    }
    
    public void setPairs(Map<MonkeyHashKey, MonkeyHashPair> pairs) {
        this.pairs = pairs;
    }

    @Override
    public String getType() {
        return HASH_OBJ;
    }

    @Override
    public String inspect() {
        List<String> list = new ArrayList<String>();
        for (MonkeyHashKey k: pairs.keySet()) {
            MonkeyHashPair v = pairs.get(k);
            String pair = String.format("%s: %s", v.getKey().inspect(), v.getValue().inspect());
            list.add(pair);
        }
        //
        StringBuilder ret = new StringBuilder();
        ret.append("{");
        ret.append(MonkeyUtil.stringJoin(", ", list));
        ret.append("}");
        //
        return ret.toString();
    }
}

class MonkeyHashKey {
    private String type;
    private int value;

    public MonkeyHashKey(String type, int value) {
        this.type = type;
        this.value = value;
    }

    @Override
    public boolean equals(Object obj) {
        if (obj instanceof MonkeyHashKey) {
            MonkeyHashKey other = (MonkeyHashKey) obj;
            if (other.type.equals(type) && other.value == value) {
                return true;
            }
        }
        return false;
    }

    @Override
    public int hashCode() {
        String h = String.format("%s-%s", type, value);
        return h.hashCode();
    }
}
    
class MonkeyHashPair {
    private MonkeyObject key;
    private MonkeyObject value;

    public MonkeyHashPair() {
        key = new MonkeyObject();
        value = new MonkeyObject();
    }
    
    public MonkeyObject getKey() {
        return key;
    }
    
    public MonkeyObject getValue() {
        return value;
    }
    
    public void setKey(MonkeyObject key) {
        this.key = key;
    }
    
    public void setValue(MonkeyObject value) {
        this.value = value;
    }
}

class MonkeyEnvironment {
    private Map<String, MonkeyObject> store;
    private Map<String, MonkeyObject> outer;

    public MonkeyEnvironment() {
        store = new HashMap<String, MonkeyObject>();
        outer = new HashMap<String, MonkeyObject>();
    }
    
    public MonkeyEnvironment(HashMap<String, MonkeyObject> outer) {
        this();
        this.outer = outer;
    }
    
    public MonkeyObject get(String name) {
        MonkeyObject obj = store.get(name);
        if (obj == null && outer != null) {
            obj = outer.get(name);
        }
        return obj;
    }
    
    public MonkeyObject set(String name, MonkeyObject value) {
        store.put(name, value);
        return value;
    }
    
    public void debug() {
        for (String k: store.keySet()) {
            MonkeyObject v = store.get(k);
            if (v != null) {
                Monkey.output(String.format("%s: %s", k, v.inspect()));
            }
        }
    }
    
    public static MonkeyEnvironment newInstance() {
        MonkeyEnvironment e = new MonkeyEnvironment();
        return e;
    }
    
    public static MonkeyEnvironment newInstanceEnclosed(MonkeyEnvironment outer) {
        MonkeyEnvironment e = new MonkeyEnvironment(MonkeyEnvironment.toMap(outer));
        return e;
    }
    
    public static HashMap<String, MonkeyObject> toMap(MonkeyEnvironment env) {
        HashMap<String, MonkeyObject> ret = new HashMap<String, MonkeyObject>();
        for (String k: env.store.keySet()) {
            MonkeyObject v = env.store.get(k);
            ret.put(k, v);
        }
        return ret;
    }
    
    public static MonkeyEnvironment fromMap(Map<String, Object> map) {
        MonkeyEnvironment e = new MonkeyEnvironment();

        for (String k: map.keySet()) {
            Object v = map.get(k);
            String key = null;
            MonkeyObject value = null;
            //
            if (k instanceof String) {
                key = k;
            } else {
                key = k.toString();
            }
            //
            if (v instanceof String) {
                value = new MonkeyObjectString((String) v);
            } else if (v instanceof Boolean) {
                value = new MonkeyObjectBoolean((Boolean) v);
            } else if (v instanceof Integer) {
                value = new MonkeyObjectInteger((Integer) v);
            } else {
                value = new MonkeyObjectString(v.toString());
            }
            //
            if (key != null && value != null) {
                e.set(key, value);
            }
        }
        return e;
    }
    
    public static MonkeyEnvironment fromDictionary(Map<String, Object> dictionary) {
        return MonkeyEnvironment.fromMap(dictionary);
    }
    
}

interface MonkeyBuiltinCallable {
    MonkeyObject call(MonkeyEvaluator evaluator, List<MonkeyObject> args);
}

class MonkeyBuiltinFunctionLen implements MonkeyBuiltinCallable {
    public MonkeyObject call(MonkeyEvaluator evaluator, List<MonkeyObject> args) {
        if (args.size() != 1) {
            return evaluator.newError(
                    String.format("wrong number of arguments, got=%s, want=1",
                            args.size()));
        }
        
        MonkeyObject a = args.get(0);
        if (a instanceof MonkeyObjectString) {
            MonkeyObjectString s = (MonkeyObjectString) a;
            MonkeyObjectInteger o = new MonkeyObjectInteger(s.getValue().length());
            return o;
        } else if (a instanceof MonkeyObjectArray) {
            MonkeyObjectArray s = (MonkeyObjectArray) a;
            MonkeyObjectInteger o = new MonkeyObjectInteger(s.getElements().size());
            return o;
        } else {
            return evaluator.newError(
                            String.format("argument to \"len\" not supported, got %s", 
                                    a.getType()));
        }
    }
}

class MonkeyBuiltinFunctionFirst implements MonkeyBuiltinCallable {
    public MonkeyObject call(MonkeyEvaluator evaluator, List<MonkeyObject> args) {
        if (args.size() != 1) {
            return evaluator.newError(
                    String.format("wrong number of arguments, got=%s, want=1",
                            args.size()));
        }
        
        MonkeyObject a = args.get(0);
        if (!(a instanceof MonkeyObjectArray)) {
            return evaluator.newError(
                            String.format("argument to \"first\" must be ARRAY, got %s", 
                                    a.getType()));
        };
        MonkeyObjectArray s = (MonkeyObjectArray) a;
        if (s.getElements().size() > 0) {
            return s.getElements().get(0);
        }
        //
        return MonkeyEvaluator.NULL;
    }
}

class MonkeyBuiltinFunctionLast implements MonkeyBuiltinCallable {
    public MonkeyObject call(MonkeyEvaluator evaluator, List<MonkeyObject> args) {
        if (args.size() != 1) {
            return evaluator.newError(
                    String.format("wrong number of arguments, got=%s, want=1",
                            args.size()));
        }
        
        MonkeyObject a = args.get(0);
        if (!(a instanceof MonkeyObjectArray)) {
            return evaluator.newError(
                            String.format("argument to \"last\" must be ARRAY, got %s", 
                                    a.getType()));
        };
        MonkeyObjectArray s = (MonkeyObjectArray) a;
        int length = s.getElements().size();
        if (length > 0) {
            return s.getElements().get(length - 1);
        }
        //
        return MonkeyEvaluator.NULL;
    }
}

class MonkeyBuiltinFunctionRest implements MonkeyBuiltinCallable {
    public MonkeyObject call(MonkeyEvaluator evaluator, List<MonkeyObject> args) {
        if (args.size() != 1) {
            return evaluator.newError(
                    String.format("wrong number of arguments, got=%s, want=1",
                            args.size()));
        }
        
        MonkeyObject a = args.get(0);
        if (!(a instanceof MonkeyObjectArray)) {
            return evaluator.newError(
                            String.format("argument to \"rest\" must be ARRAY, got %s", 
                                    a.getType()));
        };
        MonkeyObjectArray s = (MonkeyObjectArray) a;
        List<MonkeyObject> elements = s.getElements();
        int length = elements.size();
        if (length > 0) {
            List<MonkeyObject> list = new ArrayList<MonkeyObject>();
            for (int i=1; i<length; i++) {
                list.add(elements.get(i));
            }
            MonkeyObjectArray o = new MonkeyObjectArray();
            o.setElements(list);
            //
            return o;
        }
        //
        return MonkeyEvaluator.NULL;
    }
}

class MonkeyBuiltinFunctionPush implements MonkeyBuiltinCallable {
    public MonkeyObject call(MonkeyEvaluator evaluator, List<MonkeyObject> args) {
        if (args.size() != 2) {
            return evaluator.newError(
                    String.format("wrong number of arguments, got=%s, want=2",
                            args.size()));
        }
        
        MonkeyObject a = args.get(0);
        if (!(a instanceof MonkeyObjectArray)) {
            return evaluator.newError(
                            String.format("argument to \"push\" must be ARRAY, got %s", 
                                    a.getType()));
        };
        
        MonkeyObjectArray s = (MonkeyObjectArray) a;
        List<MonkeyObject> elements = s.getElements();
        int length = elements.size();
        
        List<MonkeyObject> list = new ArrayList<MonkeyObject>();
        for (int i=0; i<length; i++) {
            list.add(elements.get(i));
        }
        list.add(args.get(1));
        
        MonkeyObjectArray o = new MonkeyObjectArray();
        o.setElements(list);
        //
        return o;
    }
}

class MonkeyBuiltinFunctionPuts implements MonkeyBuiltinCallable {
    public MonkeyObject call(MonkeyEvaluator evaluator, List<MonkeyObject> args) {
        for (MonkeyObject a: args) {
            Monkey.output(a.inspectValue(), evaluator.getOutput());
        }
        //
        return MonkeyEvaluator.NULL;        
    }
}

class MonkeyBuiltins {
    public static final Map<String, MonkeyObjectBuiltin> BUILTINS;
    static {
        BUILTINS = new HashMap<String, MonkeyObjectBuiltin>();
        BUILTINS.put("len", new MonkeyObjectBuiltin(new MonkeyBuiltinFunctionLen()));
        BUILTINS.put("first", new MonkeyObjectBuiltin(new MonkeyBuiltinFunctionFirst()));
        BUILTINS.put("last", new MonkeyObjectBuiltin(new MonkeyBuiltinFunctionLast()));
        BUILTINS.put("rest", new MonkeyObjectBuiltin(new MonkeyBuiltinFunctionRest()));
        BUILTINS.put("push", new MonkeyObjectBuiltin(new MonkeyBuiltinFunctionPush()));
        BUILTINS.put("puts", new MonkeyObjectBuiltin(new MonkeyBuiltinFunctionPuts()));
    }
    
    public static MonkeyObjectBuiltin get(String name) {
        return BUILTINS.get(name);
    }
}

class MonkeyEvaluator {
    public static MonkeyObjectNull NULL = new MonkeyObjectNull();
    public static MonkeyObjectBoolean TRUE = new MonkeyObjectBoolean(true);
    public static MonkeyObjectBoolean FALSE = new MonkeyObjectBoolean(false);

    private PrintStream output;

    public MonkeyEvaluator() {
        output = System.out;
    }
    
    public MonkeyEvaluator(PrintStream output) {
        this.output = output;
    }
    
    MonkeyObject eval(Object node, MonkeyEnvironment env) {
        if (node instanceof MonkeyProgram) {
            MonkeyProgram s = (MonkeyProgram) node;
            return evalProgram(s, env);
        } else if (node instanceof MonkeyExpressionStatement) {
            MonkeyExpressionStatement s = (MonkeyExpressionStatement) node;
            return eval(s.getExpression(), env);
        } else if (node instanceof MonkeyIntegerLiteral) {
            MonkeyIntegerLiteral s = (MonkeyIntegerLiteral) node;
            MonkeyObjectInteger o = new MonkeyObjectInteger(s.getValue());
            return o;
        } else if (node instanceof MonkeyBoolean) {
            MonkeyBoolean s = (MonkeyBoolean) node;
            return getBoolean(s.getValue());
        } else if (node instanceof MonkeyPrefixExpression) {
            MonkeyPrefixExpression s = (MonkeyPrefixExpression) node;
            MonkeyObject right = eval(s.getRight(), env);
            if (isError(right)) {
                return right;
            }
            //
            return evalPrefixExpression(s.getOperator(), right);
        } else if (node instanceof MonkeyInfixExpression) {
            MonkeyInfixExpression s = (MonkeyInfixExpression) node;
            MonkeyObject left = eval(s.getLeft(), env);
            if (isError(left)) {
                return left;
            }
            //
            MonkeyObject right = eval(s.getRight(), env);
            if (isError(right)) {
                return right;
            }
            //
            return evalInfixExpression(s.getOperator(), left, right);
        } else if (node instanceof MonkeyBlockStatement) {
            MonkeyBlockStatement s = (MonkeyBlockStatement) node;
            return evalBlockStatement(s, env);
        } else if (node instanceof MonkeyIfExpression) {
            MonkeyIfExpression s = (MonkeyIfExpression) node;
            return evalIfExpression(s, env);
        } else if (node instanceof MonkeyReturnStatement) {
            MonkeyReturnStatement s = (MonkeyReturnStatement) node;
            MonkeyObject val = eval(s.getReturnValue(), env);
            if (isError(val)) {
                return val;
            }
            //
            MonkeyObjectReturnValue o = new MonkeyObjectReturnValue();
            o.setValue(val);
            return o;
        } else if (node instanceof MonkeyLetStatement) {
            MonkeyLetStatement s = (MonkeyLetStatement) node;
            MonkeyObject val = eval(s.getValue(), env);
            if (isError(val)) {
                return val;
            }
            //
            env.set(s.getName().getValue(), val);
        } else if (node instanceof MonkeyIdentifier) {
            MonkeyIdentifier s = (MonkeyIdentifier) node;
            return evalIdentifier(s, env);
        } else if (node instanceof MonkeyFunctionLiteral) {
            MonkeyFunctionLiteral s = (MonkeyFunctionLiteral) node;
            List<MonkeyIdentifier> params = s.getParameters();
            MonkeyBlockStatement body = s.getBody();
            //
            MonkeyObjectFunction o = new MonkeyObjectFunction();
            o.setParameter(params);
            o.setBody(body);
            o.setEnvironment(env);
            return o;
        } else if (node instanceof MonkeyCallExpression) {
            MonkeyCallExpression s = (MonkeyCallExpression) node;
            MonkeyObject function = eval(s.getFunction(), env);
            if (isError(function)) {
                return function;
            }
            //
            List<MonkeyObject> args = evalExpressions(s.getArguments(), env);
            if (args.size() == 1 && isError(args.get(0))) {
                return args.get(0);
            }
            //
            return applyFunction(function, args);
        } else if (node instanceof MonkeyStringLiteral) {
            MonkeyStringLiteral s = (MonkeyStringLiteral) node;
            MonkeyObjectString o = new MonkeyObjectString(s.getValue());
            return o;
        } else if (node instanceof MonkeyArrayLiteral) {
            MonkeyArrayLiteral s = (MonkeyArrayLiteral) node;
            List<MonkeyObject> elements = evalExpressions(s.getElements(), env);
            if (elements.size() == 1 && isError(elements.get(0))) {
                return elements.get(0);
            }
            //
            MonkeyObjectArray o = new MonkeyObjectArray();
            o.setElements(elements);
            return o;
        } else if (node instanceof MonkeyIndexExpression) {
            MonkeyIndexExpression s = (MonkeyIndexExpression) node;
            MonkeyObject left = eval(s.getLeft(), env);
            if (isError(left)) {
                return left;
            }
            //
            MonkeyObject index = eval(s.getIndex(), env);
            if (isError(index)) {
                return index;
            }
            //
            return evalIndexExpression(left, index);
        } else if (node instanceof MonkeyHashLiteral) {
            MonkeyHashLiteral s = (MonkeyHashLiteral) node;
            return evalHashLiteral(s, env);
        }
        
        return null;
    }

    MonkeyObject evalProgram(MonkeyProgram program, MonkeyEnvironment env) {
        MonkeyObject ret = new MonkeyObject();
        for (MonkeyStatement s: program.getStatements()) {
            ret = eval(s, env);
            //
            if (ret instanceof MonkeyObjectReturnValue) {
                MonkeyObjectReturnValue o = (MonkeyObjectReturnValue) ret;
                return o.getValue();
            } else if (ret instanceof MonkeyObjectError) {
                MonkeyObjectError o = (MonkeyObjectError) ret;
                return o;
            }
        }
        return ret;
    }
    
    MonkeyObject evalBlockStatement(MonkeyBlockStatement block, MonkeyEnvironment env) {
        MonkeyObject ret = new MonkeyObject();
        for (MonkeyStatement s: block.getStatements()) {
            ret = eval(s, env);
            //
            if (ret != null) {
                String type = ret.getType();
                if (type.equals(MonkeyObject.RETURN_VALUE_OBJ) || type.equals(MonkeyObject.ERROR_OBJ)) {
                    return ret;
                }
            }
        }
        return ret;
    }

    MonkeyObject getBoolean(boolean value) {
        if (value) {
            return TRUE;
        }
        //
        return FALSE;
    }

    MonkeyObject evalPrefixExpression(String operator, MonkeyObject right) {
        if (operator.equals("!")) {
            return evalBangOperatorExpression(right);
        } else if (operator.equals("-")) {
            return evalMinusPrefixOperatorExpression(right);
        }
        return newError(String.format("unknown operator: %s%s", operator, right.getType()));
    }

    MonkeyObject evalInfixExpression(String operator, MonkeyObject left, MonkeyObject right) {
        if (left.getType().equals(MonkeyObject.INTEGER_OBJ) && 
                right.getType().equals(MonkeyObject.INTEGER_OBJ)) {
            return evalIntegerInfixExpression(operator, (MonkeyObjectInteger)left, 
                    (MonkeyObjectInteger)right);
        } else if (left.getType().equals(MonkeyObject.STRING_OBJ) &&
                right.getType().equals(MonkeyObject.STRING_OBJ)) {
            return evalStringInfixExpression(operator, (MonkeyObjectString)left, 
                    (MonkeyObjectString)right);
        } else if (operator.equals("==")) {
            return getBoolean(left == right);
        } else if (operator.equals("!=")) {
            return getBoolean(left != right);
        } else if (!left.getType().equals(right.getType())) {
            return newError(String.format("type mismatch: %s %s %s", 
                    left.getType(), operator, right.getType()));
        }
        return newError(String.format("unknown operator: %s %s %s", 
                    left.getType(), operator, right.getType()));
    }
    
    MonkeyObject evalIntegerInfixExpression(String operator, 
            MonkeyObjectInteger left, MonkeyObjectInteger right) {
        int leftVal = left.getValue();
        int rightVal = right.getValue();
        //
        MonkeyObjectInteger o = new MonkeyObjectInteger();
        if (operator.equals("+")) {
            o.setValue(leftVal + rightVal);
            return o;
        } else if (operator.equals("-")) {
            o.setValue(leftVal - rightVal);
            return o;
        } else if (operator.equals("*")) {
            o.setValue(leftVal * rightVal);
            return o;
        } else if (operator.equals("/")) {
            try {
                o.setValue(leftVal / rightVal);
                return o;
            } catch (ArithmeticException e) {
                return NULL;
            }
        } else if (operator.equals("<")) {
            return getBoolean(leftVal < rightVal);
        } else if (operator.equals(">")) {
            return getBoolean(leftVal > rightVal);
        } else if (operator.equals("==")) {
            return getBoolean(leftVal == rightVal);
        } else if (operator.equals("!=")) {
            return getBoolean(leftVal != rightVal);
        }
        return newError(String.format("unknown operator: %s %s %s", left.getType(),
                operator, right.getType()));
    }

    MonkeyObject evalStringInfixExpression(String operator, 
            MonkeyObjectString left, MonkeyObjectString right) {
        String leftVal = left.getValue();
        String rightVal = right.getValue();
        //
        MonkeyObjectString o = new MonkeyObjectString();
        if (!operator.equals("+")) {
            return newError(String.format("unknown operator: %s %s %s", 
                    left.getType(), operator, right.getType()));
        }
        //
        o.setValue(leftVal + rightVal);
        return o;
    }
    
    MonkeyObject evalBangOperatorExpression(MonkeyObject right) {
        if (right == TRUE) {
            return FALSE;
        } else if (right == FALSE) {
            return TRUE;
        } else if (right == NULL) {
            return TRUE;
        }
        return FALSE;
    }

    MonkeyObject evalMinusPrefixOperatorExpression(MonkeyObject right) {
        if (!right.getType().equals(MonkeyObject.INTEGER_OBJ)) {
            return newError(String.format("unknown operator: -%s", right.getType()));
        }
        //
        MonkeyObjectInteger o = new MonkeyObjectInteger();
        int val = ((MonkeyObjectInteger) right).getValue();
        o.setValue(-val);
        return o;
    }

    MonkeyObject evalIfExpression(MonkeyIfExpression expression, MonkeyEnvironment env) {
        MonkeyObject condition = eval(expression.getCondition(), env);
        if (isError(condition)) {
            return condition;
        }
        //
        if (isTruthy(condition)) {
            return eval(expression.getConsequence(), env);
        } else if (!expression.getAlternative().isEmpty()) {
            return eval(expression.getAlternative(), env);
        } else {
            return NULL;
        }
    }
    
    MonkeyObject evalIdentifier(MonkeyIdentifier ident, MonkeyEnvironment env) {
        MonkeyObject val = env.get(ident.getValue());
        if (val != null) {
            return val;
        }
        //
        MonkeyObjectBuiltin builtin = MonkeyBuiltins.get(ident.getValue());
        if (builtin != null) {
            return builtin;
        }
        //
        return newError(String.format("identifier not found: %s", ident.getValue()));
    }
    
    List<MonkeyObject> evalExpressions(List<MonkeyExpression> exp, MonkeyEnvironment env) {
        List<MonkeyObject> result = new ArrayList<MonkeyObject>();
        //
        for (MonkeyExpression e: exp) {
            MonkeyObject evaluated = eval(e, env);
            if (isError(evaluated)) {
                result.add(evaluated);
                return result;
            }
            result.add(evaluated);
        }
        //
        return result;
    }
    
    MonkeyObject evalIndexExpression(MonkeyObject left, MonkeyObject index) {
        if (left.getType().equals(MonkeyObject.ARRAY_OBJ) &&
                index.getType().equals(MonkeyObject.INTEGER_OBJ)) {
            return evalArrayIndexExpression((MonkeyObjectArray)left, 
                    (MonkeyObjectInteger)index);
        } else if (left.getType().equals(MonkeyObject.HASH_OBJ)) {
            return evalHashIndexExpression((MonkeyObjectHash)left, index);
        }
        return newError(String.format("index operator not supported: %s", 
                left.getType()));
    }
    
    MonkeyObject evalArrayIndexExpression(MonkeyObjectArray array, 
            MonkeyObjectInteger index) {
        int idx = index.getValue();
        int max = array.getElements().size() - 1;
        //
        if (idx < 0 || idx > max) {
            return NULL;
        }
        //
        return array.getElements().get(idx);
    }
    
    MonkeyObject evalHashLiteral(MonkeyHashLiteral node, MonkeyEnvironment env) {
        Map<MonkeyHashKey, MonkeyHashPair> pairs = new HashMap<MonkeyHashKey, MonkeyHashPair>();
        //
        for (MonkeyExpression k: node.getPairs().keySet()) {
            MonkeyObject key = eval(k, env);
            if (isError(key)) {
                return key;
            }
            //
            if (!(key instanceof MonkeyHashable)) {
                return newError(String.format("unusable as hash key: %s", 
                        key.getType()));
            }
            //
            MonkeyExpression v = node.getPairs().get(k);
            MonkeyObject val = eval(v, env);
            if (isError(val)) {
                return val;
            }
            //
            MonkeyHashKey hashed = ((MonkeyHashable)key).hashKey();
            MonkeyHashPair p = new MonkeyHashPair();
            p.setKey(key);
            p.setValue(val);
            pairs.put(hashed, p);
        }
        //
        MonkeyObjectHash o = new MonkeyObjectHash();
        o.setPairs(pairs);
        return o;
    }
    
    MonkeyObject evalHashIndexExpression(MonkeyObjectHash hashtable, MonkeyObject index) {
        if (!(index instanceof MonkeyHashable)) {
            return newError(String.format("unusable as hash key: %s", index.getType()));
        }
        //
        MonkeyHashable hashIndex = (MonkeyHashable)index;
        MonkeyHashPair pair = hashtable.getPairs().get(hashIndex.hashKey());
        if (pair == null) {
            return NULL;
        }
        //
        return pair.getValue();
    }
    
    MonkeyObject applyFunction(MonkeyObject fn, List<MonkeyObject> args) {
        if (fn instanceof MonkeyObjectFunction) {
            MonkeyObjectFunction f = (MonkeyObjectFunction)fn;
            MonkeyEnvironment extendedEnv = extendFunctionEnv(f, args);
            MonkeyObject evaluated = eval(f.getBody(), extendedEnv);
            return unwrapReturnValue(evaluated);
        } else if (fn instanceof MonkeyObjectBuiltin) {
            MonkeyObjectBuiltin f = (MonkeyObjectBuiltin)fn;
            MonkeyBuiltinCallable c = f.getFn();
            return c.call(this, args);
        }
        //
        return newError(String.format("not a function: %s", fn.getType()));
    }

    MonkeyEnvironment extendFunctionEnv(MonkeyObjectFunction fn, 
            List<MonkeyObject> args) {
        MonkeyEnvironment env = MonkeyEnvironment.newInstanceEnclosed(fn.getEnvironment());
        for (int i=0; i<fn.getParameters().size(); i++) {
            MonkeyIdentifier param = fn.getParameters().get(i);
            env.set(param.getValue(), args.get(i));
        }
        //
        return env;
    }

    MonkeyObject unwrapReturnValue(MonkeyObject obj) {
        if (obj instanceof MonkeyObjectReturnValue) {
            MonkeyObjectReturnValue o = (MonkeyObjectReturnValue)obj;
            return o.getValue();
        }
        //
        return obj;
    }
    
    boolean isTruthy(MonkeyObject obj) {
        if (obj == NULL) {
            return false;
        } else if (obj == TRUE) {
            return true;
        } else if (obj == FALSE) {
            return false;
        } else {
            return true;
        }
    }
    
    MonkeyObject newError(String message) {
        MonkeyObjectError ret = new MonkeyObjectError();
        ret.setMessage(message);
        return ret;
    }
    
    boolean isError(MonkeyObject obj) {
        if (obj != null) {
            return obj.getType().equals(MonkeyObject.ERROR_OBJ);
        }
        //
        return false;
    }

    public PrintStream getOutput() {
        return output;
    }

    public void setOutput(PrintStream output) {
        this.output = output;
    }
    
    public static MonkeyEvaluator newInstance() {
        return new MonkeyEvaluator();
    }        
}

class MonkeyUtil {
    public static String stringJoin(String delimiter, List list) {
        StringBuilder ret = new StringBuilder();
        //
        int max = list.size();
        for (int i=0; i<max; i++) {
            Object o = list.get(i);
            ret.append(o.toString());
            
            if (i < max-1) {
                ret.append(delimiter);
            }
        }
        //
        return ret.toString();
    }
    
    public static String readFile(File f) {
        StringBuilder ret = new StringBuilder();
        //
        try {
            Scanner scan = new Scanner(f);
            while (scan.hasNextLine()) {
                String line = scan.nextLine();
                ret.append(line);
            }
            scan.close();
        } catch (Exception e) {
        }
        //
        return ret.toString();
    }
}

class Monkey {
    public static final String VERSION = "0.2";
    public static final String TITLE = "Monkey.java " + VERSION;
    public static final String MESSAGE = "Press ENTER to quit";
    public static final String LINESEP = System.getProperty("line.separator");
    public static final String PROMPT = ">> ";
    
    public static String input(String s) {
        Scanner scan = new Scanner(System.in);
        System.out.print(s);
        try {
            return scan.nextLine();
        } catch (Exception e) {
            return "";
        }
    }
    
    public static void output(String s) {
        output(s, System.out);
    }

    public static void output(String s, PrintStream output) {
        output.println(s);
    }
    
    public static void lexer() {
        Monkey.output(TITLE);
        Monkey.output(MESSAGE);
        while (true) {
            String inp = Monkey.input(PROMPT).trim();
            if (inp.length() == 0) {
                break;
            }
            MonkeyLexer l = MonkeyLexer.newInstance(inp);
            while (true) {
                MonkeyToken t = l.nextToken();
                if (t.getType().equals(MonkeyToken.EOF)) {
                    break;
                }
                Monkey.output(String.format("Type: %s, Literal: %s", 
                        t.getType(), t.getLiteral()));
            }
        }
    }

    public static void parser() {
        Monkey.output(TITLE);
        Monkey.output(MESSAGE);
        while (true) {
            String inp = Monkey.input(PROMPT).trim();
            if (inp.length() == 0) {
                break;
            }
            MonkeyLexer l = MonkeyLexer.newInstance(inp);
            MonkeyParser p = MonkeyParser.newInstance(l);
            MonkeyProgram program = p.parseProgram();
            //
            List<String> errors = p.getErrors();
            if (!errors.isEmpty()) {
                Monkey.printParseErrors(errors);
                continue;
            }
            //
            Monkey.output(program.toString());
        }
    }
    
    public static void printParseErrors(List<String> errors) {
        for (String e: errors) {
            Monkey.output(String.format("PARSER ERROR: %s", e));
        }
    }

    public static void printParseErrors(List<String> errors, PrintStream output) {
        for (String e: errors) {
            Monkey.output(String.format("PARSER ERROR: %s", e), output);
        }
    }
    
    public static void evaluator() {
        Monkey.output(TITLE);
        Monkey.output(MESSAGE);
        MonkeyEnvironment env = MonkeyEnvironment.newInstance();
        while (true) {
            String inp = Monkey.input(PROMPT).trim();
            if (inp.length() == 0) {
                break;
            }
            MonkeyLexer l = MonkeyLexer.newInstance(inp);
            MonkeyParser p = MonkeyParser.newInstance(l);
            MonkeyProgram program = p.parseProgram();
            //
            List<String> errors = p.getErrors();
            if (!errors.isEmpty()) {
                Monkey.printParseErrors(errors);
                continue;
            }
            MonkeyEvaluator evaluator = MonkeyEvaluator.newInstance();
            MonkeyObject evaluated = evaluator.eval(program, env);
            if (evaluated != null) {
                Monkey.output(evaluated.inspect());
            }
        }
    }
    
    public static void evaluatorString(String s, MonkeyEnvironment environ, PrintStream output) {
        MonkeyEnvironment env;
        if (environ == null || !(environ instanceof MonkeyEnvironment)) {
            env = MonkeyEnvironment.newInstance();
        } else {
            env = environ;
        }
        MonkeyLexer l = MonkeyLexer.newInstance(s);
        MonkeyParser p = MonkeyParser.newInstance(l);
        MonkeyProgram program = p.parseProgram();
        //
        List<String> errors = p.getErrors();
        if (!errors.isEmpty()) {
            Monkey.printParseErrors(errors, output);
            return;
        }
        //
        MonkeyEvaluator evaluator = MonkeyEvaluator.newInstance();
        evaluator.setOutput(output);
        MonkeyObject evaluated = evaluator.eval(program, env);
        if (evaluated != null) {
            Monkey.output(evaluated.inspect(), output);
        }
    }

    public static void main(String[] args) {
        if (args.length < 1) {
            Monkey.evaluator();
        } else {
            String t = args[0];
            String s = t;
            File f = new File(t);
            if (f.exists()) {
                try {
                    s = MonkeyUtil.readFile(f);
                } catch (Exception e) {
                }
            }
            if (s.length() > 0) {
                Monkey.evaluatorString(s, null, System.out);
            }
        }
    }
}
