from rply import ParserGenerator, LexerGenerator
from rply.token import BaseBox


class BoxString(BaseBox):
    def __init__(self, value):
        self.value = value
    def getstr(self):
        return self.value


lg = LexerGenerator()

lg.add('GT', r'\bgt\b')
lg.add('GE', r'\bge\b')
lg.add('LT', r'\blt\b')
lg.add('LE', r'\ble\b')

lg.add('EQ', r'\beq\b')
lg.add('NE', r'\bne\b')
lg.add('IS', r'\bis\b')
lg.add('LIKE', r'\blike\b')

lg.add('AND', r'\band\b')
lg.add('OR', r'\bor\b')
lg.add('NOT', r'\bnot\b')

lg.add('NONE', r'\bnull\b')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')
lg.add('NUMBER', r'[\d]{1,99}([.]\d{1,99})?')
lg.add('STRING', r'"[^"]*"')
lg.add('NAME', r'[a-zA-Z_]\w*(\.[a-zA-Z_]\w*)?')

lg.ignore(r'\s+')
lexer = lg.build()

pg = ParserGenerator(
    # A list of all token names, accepted by the parser.
    ['NAME', 'NUMBER', 'STRING', 'NONE',
     'GT', 'GE', 'LT', 'LE',
     'EQ', 'NE', 'IS', 'LIKE',
     'AND', 'OR', 'NOT',
     'OPEN_PARENS', 'CLOSE_PARENS'],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['OR']),
        ('left', ['AND']),
        ('left', ['EQ', 'NE', 'IS']),
        ('left', ['GT', 'GE', 'LT', 'LE']),
        ('right', ['NOT'])
    ]
)


@pg.production('expression : expression AND expression')
@pg.production('expression : expression OR expression')
@pg.production('expression : NOT expression')
@pg.production('expression : OPEN_PARENS expression CLOSE_PARENS')
def exp_and_or(p):
    s = ' '.join(map(lambda x: x.getstr(), p))
    return BoxString(s)


@pg.production('expression : NAME GT value')
@pg.production('expression : NAME GE value')
@pg.production('expression : NAME LT value')
@pg.production('expression : NAME LE value')
@pg.production('expression : NAME EQ value')
@pg.production('expression : NAME NE value')
def expression(p):
    op = p[1].getstr()
    if op == 'gt':
        op = '>'
    elif op == 'ge':
        op = '>='
    elif op == 'lt':
        op = '<'
    elif op == 'le':
        op = '<='
    elif op == 'eq':
        op = '='
    elif op == 'ne':
        op = '!='
    s = ' '.join([p[0].getstr(), op, p[2].getstr()])
    return BoxString(s)


@pg.production('expression : NAME IS NONE')
@pg.production('expression : NAME IS NOT NONE')
def exp_is(p):
    s = ' '.join([x.getstr() for x in p])
    return BoxString(s)


@pg.production('expression : NAME LIKE STRING')
def exp_like(p):
    val = p[2].getstr()
    val = '"%{}%"'.format(val.strip('"'))
    s = '{} {} {}'.format(
            p[0].getstr(),
            p[1].getstr(),
            val
        )
    return BoxString(s)


@pg.production('value : NUMBER')
@pg.production('value : STRING')
@pg.production('value : NONE')
def exp_value(p):
    return p[0]


parser = pg.build()


if __name__ == '__main__':
    print(parser.parse(lexer.lex('ctime gt "2017-12-13 13:53:06"')).value)
    print(parser.parse(lexer.lex('x eq 1')).value)
    print(parser.parse(lexer.lex('x like "abc"')).value)
    print(parser.parse(lexer.lex('x is null')).value)
    print(parser.parse(lexer.lex('not x ne 1')).value)
    print(parser.parse(lexer.lex('x ne 1 or y eq 3')).value)
    print(parser.parse(lexer.lex('x eq 2 and (y eq 24 or z eq 24)')).value)
    print(parser.parse(lexer.lex('level eq 2 and (src_id eq 24 or root_id eq 24)')).value)
    print(parser.parse(lexer.lex('(x ne 1 or y eq 3) and z eq 0')).value)
