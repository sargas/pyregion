import os
from .core import Circle
from ._parsing_helpers import DS9ParsingException


class DS9Parser:
    def __init__(self):
        if 'parser' not in DS9Parser.__dict__:
            DS9Parser._parser, DS9Parser._lexer = self.make_parser()

    @classmethod
    def make_parser(cls):
        from astropy.extern.ply import lex, yacc

        literals = ['(', ')', ';', ',']
        tokens = (
            'PROPERTY',
            'CIRCLE',
            'DELIMITER'
        )
        states = (
            ('proplist', 'exclusive'),
        )

        def t_CIRCLE(t):
            r'circle'
            t.lexer.begin('proplist')
            t.value = Circle
            return t

        def t_proplist_PROPERTY(t):
            r'[\d.:hdms"\'pir]+'
            return t

        def t_proplist_DELIMITER(t):
            r'[\n;]'
            t.lexer.begin('INITIAL')
            return t

        def t_error(t):
            raise DS9ParsingException(t)

        t_proplist_error = t_error

        t_ignore = ' \t'
        t_proplist_ignore = t_ignore

        def p_shapes(p):
            ''' shapes : shapes DELIMITER shape
                       | shape'''
            if len(p) == 2 and p[1] is not None:
                p[0] = [p[1]]
            elif len(p) == 4:
                if p[3] is not None:
                    p[0] = p[1] + [p[3]]
                else:
                    p[0] = p[1]

        def p_shape(p):
            ''' shape : circle
                      | '''
            if len(p) == 2:
                p[0] = p[1]

        def p_proplist(p):
            '''proplist : proplist PROPERTY
                        | proplist ',' PROPERTY '''
            property_value = p[len(p)-1]
            p[0] = p[1] + [property_value]

        def p_proplist_single(p):
            'proplist : PROPERTY'
            p[0] = [p[1]]

        def p_proplist_parens(p):
            "proplist : '(' proplist ')' "
            p[0] = p[2]

        def p_circle(p):
            'circle : CIRCLE proplist'
            p[0] = p[1].from_coordlist(p[2], "", 'icrs')

        lexer = lex.lex(debug=True)
        parser = yacc.yacc(debug=True)
        return parser, lexer
        try:
            from . import ds9_lextab
            lexer = lex.lex(optimize=True, lextab=ds9_lextab)
        except ImportError:
            lexer = lex.lex(optimize=True, lextab='ds9_lextab',
                            outputdir=os.path.dirname(__file__))

        try:
            raise ImportError
            from . import ds9_parsetab
            parser = yacc.yacc(debug=False, tabmodule=ds9_parsetab,
                               write_tables=False)
        except ImportError:
            parser = yacc.yacc(debug=False, tabmodule='ds9_parsetab',
                               outputdir=os.path.dirname(__file__))

        return parser, lexer

    def parse(self, data, debug=False):
        return self._parser.parse(data, lexer=self._lexer, debug=debug)
