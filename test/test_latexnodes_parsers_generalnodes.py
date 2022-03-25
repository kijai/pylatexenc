import unittest
import sys
import logging


from pylatexenc.latexnodes.parsers._generalnodes import (
    LatexGeneralNodesParser,
    LatexSingleNodeParser,
)

from pylatexenc.latexnodes import (
    LatexWalkerTokenParseError,
    LatexTokenReader,
    LatexToken,
    ParsingState,
    ParsedMacroArgs,
)
from pylatexenc.latexnodes.nodes import *


from ._helpers_tests import (
    DummyWalker,
    DummyLatexContextDb,
)


# ------------------------------------------------------------------------------


class TestGeneralNodesParser(unittest.TestCase):

    def test_gets_nodes_with_stuff(self):
        latextext = r'''Hello there, \yourname. What's that about {}?'''

        tr = LatexTokenReader(latextext)
        ps = ParsingState(s=latextext, latex_context=DummyLatexContextDb())
        lw = DummyWalker()

        parser = LatexGeneralNodesParser()

        nodes, carryover_info = lw.parse_content(parser, token_reader=tr, parsing_state=ps)

        self.assertEqual(
            nodes,
            LatexNodeList([
                LatexCharsNode(
                    parsing_state=ps,
                    chars='Hello there, ',
                    pos=0,
                    pos_end=37-24,
                ),
                LatexMacroNode(
                    parsing_state=ps,
                    macroname='yourname',
                    nodeargd=ParsedMacroArgs(),
                    macro_post_space='',
                    spec=ps.latex_context.get_macro_spec('yourname'),
                    pos=37-24,
                    pos_end=46-24,
                ),
                LatexCharsNode(
                    parsing_state=ps,
                    chars=". What's that about ",
                    pos=46-24,
                    pos_end=66-24,
                ),
                LatexGroupNode(
                    parsing_state=ps,
                    delimiters=('{','}'),
                    nodelist=LatexNodeList(
                        [
                            # LatexCharsNode(
                            #     parsing_state=ps,
                            #     chars="A",
                            #     pos=67-24,
                            #     pos_end=68-24,
                            # ),
                        ],
                        pos='<POS>',
                        pos_end='<POS_END>',
                    ),
                    pos=66-24,
                    pos_end=68-24,
                ),
                LatexCharsNode(
                    parsing_state=ps,
                    chars="?",
                    pos=68-24,
                    pos_end=69-24,
                ),
            ])
        )


# ------------------------------------------------------------------------------

class TestSingleNodeParser(unittest.TestCase):
    def test_simple(self):
        latextext = r'''Hello there, \yourname. What's that about {}?'''

        tr = LatexTokenReader(latextext)
        ps = ParsingState(s=latextext, latex_context=DummyLatexContextDb())
        lw = DummyWalker()

        parser = LatexSingleNodeParser()

        nodes, carryover_info = lw.parse_content(parser, token_reader=tr, parsing_state=ps)

        self.assertEqual(
            nodes,
            LatexNodeList([
                LatexCharsNode(
                    parsing_state=ps,
                    chars='Hello there, ',
                    pos=0,
                    pos_end=37-24,
                ),
            ])
        )

    def test_simple_get_comment(self):
        latextext = r'''% comment here.
Hello there, \yourname. What's that about {}?'''

        tr = LatexTokenReader(latextext)
        ps = ParsingState(s=latextext, latex_context=DummyLatexContextDb())
        lw = DummyWalker()

        parser = LatexSingleNodeParser() #stop_on_comment=True

        nodes, carryover_info = lw.parse_content(parser, token_reader=tr, parsing_state=ps)

        self.assertEqual(
            nodes,
            LatexNodeList([
                LatexCommentNode(
                    parsing_state=ps,
                    comment=' comment here.',
                    comment_post_space='\n',
                    pos=0,
                    pos_end=40-24,
                ),
            ])
        )
        

    def test_simple_skip_comment(self):
        latextext = r'''% comment here.
Hello there, \yourname. What's that about {}?'''

        tr = LatexTokenReader(latextext)
        ps = ParsingState(s=latextext, latex_context=DummyLatexContextDb())
        lw = DummyWalker()

        parser = LatexSingleNodeParser(stop_on_comment=False)

        nodes, carryover_info = lw.parse_content(parser, token_reader=tr, parsing_state=ps)

        self.assertEqual(
            nodes,
            LatexNodeList([
                LatexCommentNode(
                    parsing_state=ps,
                    comment=' comment here.',
                    comment_post_space='\n',
                    pos=0,
                    pos_end=40-24,
                ),
                LatexCharsNode(
                    parsing_state=ps,
                    chars='Hello there, ',
                    pos=16,
                    pos_end=16+13,
                ),
            ])
        )
        










if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
#
