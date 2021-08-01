from typing import Iterator

from lark import Token, Lark
from lark.lark import PostLex

base_grammar = """

start: statement+

statement: CNAME "=" expr

?expr: (expr "+")? mul
?mul: (mul "*")? atom

?atom: "(" expr ")"
     | CNAME
    
LINE_DIRECTIVE: "#line"

%import common.CNAME
%import common.WS
%import common.SIGNED_INT
%ignore WS
"""


class CarryOverPosition(PostLex):
    always_accept = ('LINE_DIRECTIVE', 'SIGNED_INT')

    def process(self, stream: Iterator[Token]) -> Iterator[Token]:
        current_relative_offset = 0

        for token in stream:
            if token.type == 'LINE_DIRECTIVE':
                try:
                    line_number = int(next(stream))
                except (StopIteration, ValueError):
                    raise ValueError("Malformed line_directive")
                current_relative_offset = line_number-token.line
            else:
                token.line += current_relative_offset
                token.end_line += current_relative_offset
                yield token


parser = Lark(base_grammar, parser='lalr', postlex=CarryOverPosition(), propagate_positions=True)

tree = parser.parse("""
#line 100
a = a

#line 50
b = a 
+ b

#line -1
c = a *
 #line 100
 (b 
+ c)
""")

for c in tree.children:
    print(c.meta.line, c.meta.end_line)