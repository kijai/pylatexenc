# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
# 
# Copyright (c) 2022 Philippe Faist
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

# Internal module. Internal API may move, disappear or otherwise change at any
# time and without notice.

from __future__ import print_function, unicode_literals

import logging
logger = logging.getLogger(__name__)

from ..latexnodes.parsers import get_standard_argument_parser, LatexParserBase

from ..latexnodes import (
    ParsedMacroArgs,
)


# for Py3
_basestring = str

### BEGIN_PYTHON2_SUPPORT_CODE
import sys
if sys.version_info.major == 2:
    # Py2
    _basestring = basestring
### END_PYTHON2_SUPPORT_CODE




class LatexArgumentSpec(object):
    r"""
    Specify an argument accepted by a callable (a macro, an environment, or
    specials).

    .. py:attribute:: parser

       The parser instance to use to parse an argument to this callable.

       For the constructor you can also specify a string represending a standard
       argument type, such as '{', '[', '*', or also some `xparse`-inspired
       strings.  See
       :py:class:`~pylatexenc.latexnodes.parsers.LatexStandardArgumentParser`.
       In this case, a suitable parser is instanciated and stored in the
       `parser` attribute.

    .. py:attribute:: argname

       A name for the argument (which can be `None`, if the argument is to be
       referred to only by number).

       The name can serve for easier argument lookups and can offer more
       future-proof flexibility: E.g., while adding more optional arguments
       renumbers all arguments, you can refer to them by name to avoid having to
       update all references to argument numbers.

       (TODO: Still need good lookup functions in :py:class:`ParsedMacroArgs`,
       etc.)
    """
    def __init__(self, parser, argname=None):

        self.parser = parser

        if isinstance(parser, _basestring):
            self.arg_node_parser = get_standard_argument_parser(parser)
        else:
            self.arg_node_parser = parser # it's directly the parser instance.

        self.argname = argname


    def __repr__(self):
        return "{cls}(argname={argname!r}, parser={parser!r})".format(
            cls=self.__class__.__name__,
            argname=self.argname,
            parser=self.parser
        )

    def to_json_object(self):
        if self.argname:
            return dict(argname=self.argname, parser=self.parser)
        return dict(parser=self.parser)
        
    def __eq__(self, other):
        return (
            self.parser == other.parser
            and self.argname == other.argname
        )


class LatexNoArgumentsParser(LatexParserBase):
    r"""
    Convenience class for whenever there are no arguments to parse at all.
    """

### BEGIN_PYLATEXENC2_LEGACY_SUPPORT_CODE
    @property
    def argspec(self):
        return ''
### END_PYLATEXENC2_LEGACY_SUPPORT_CODE

    def __call__(self, latex_walker, token_reader, parsing_state, **kwargs):

        parsed = ParsedMacroArgs(
            arguments_spec_list=[],
            argnlist=[],
            # pos=token_reader.cur_pos(),
            # pos_end=token_reader.cur_pos()
        )

        return parsed, None

    def __eq__(self, other):
        return self.__class__ is other.__class__


class LatexArgumentsParser(LatexParserBase):
    r"""
    A parser class that handles the arguments of a callable (a macro, an
    environment, or specials).

    ........................

    The parser's main function (:py:meth:`__call__()`) produces a
    :py:class:`~pylatexenc.latexnodes.ParsedMacroArgs` instance.

    Any parser carry-over information generated by individual argument parsers
    is ignored (with a warning).


    .. py:attribute:: arguments_spec_list

       A list of :py:class:`LatexArgumentSpec` instances describing a sequence
       of arguments (along with suitable parsers) that a given callable accepts.

       The constructor expects an iterable of elements that are either already
       :py:class:`LatexArgumentSpec` instances, or that are a string
       representing a standard argument type, in which case the string is used
       to construct a :py:class:`LatexArgumentSpec` (see doc for that class).
    """

    def __init__(self,
                 arguments_spec_list,
                 **kwargs
                 ):
        super(LatexArgumentsParser, self).__init__(**kwargs)

        if arguments_spec_list is None:
            arguments_spec_list = []

        self.arguments_spec_list = [
            (LatexArgumentSpec(arg) if not isinstance(arg, LatexArgumentSpec) else arg)
            for arg in arguments_spec_list
        ]

### BEGIN_PYLATEXENC2_LEGACY_SUPPORT_CODE
    @property
    def argspec(self):
        from ..latexnodes._parsedargs import _argspec_from_arguments_spec_list
        return _argspec_from_arguments_spec_list(self.arguments_spec_list)
### END_PYLATEXENC2_LEGACY_SUPPORT_CODE

    def __call__(self, latex_walker, token_reader, parsing_state, **kwargs):

        argnlist = []

        pos_start_default = token_reader.cur_pos()
        pos_start = None
        last_arg_node = None

        for argj, arg in enumerate(self.arguments_spec_list):

            logger.debug("Parsing argument %d / %s", argj,
                         arg.arg_node_parser.__class__.__name__)

            peeked_token = token_reader.peek_token_or_none(parsing_state=parsing_state)

            arg_node_parser = arg.arg_node_parser
            argnodes, parsing_state_delta = latex_walker.parse_content(
                arg_node_parser,
                token_reader,
                parsing_state,
                open_context=(
                    "Argument {}".format(argj),
                    peeked_token
                )
            )
            if parsing_state_delta is not None:
                logger.warning(
                    "Parsing state changes information (%r) ignored in arguments!",
                    parsing_state_delta
                )
            argnlist.append( argnodes )

            if argnodes is not None:
                if pos_start is None:
                    pos_start = argnodes.pos
                last_arg_node = argnodes

        if pos_start is not None and last_arg_node is not None:
            pos = pos_start
            pos_end = last_arg_node.pos_end
        else:
            pos = pos_start_default
            pos_end = pos

        parsed = ParsedMacroArgs(
            arguments_spec_list=self.arguments_spec_list,
            argnlist=argnlist,
            # pos=pos,
            # pos_end=pos_end
        )

        logger.debug("Parsed arguments = %r", parsed)

        return parsed, None


    def __eq__(self, other):
        return (
            self.__class__ is other.__class__
            and self.arguments_spec_list == other.arguments_spec_list
        )



# ------------------------------------------------------------------------------

### BEGIN_PYLATEXENC2_LEGACY_SUPPORT_CODE


class _LegacyPyltxenc2MacroArgsParserWrapper(LatexParserBase):
    def __init__(self, args_parser, spec_object):
        super(_LegacyPyltxenc2MacroArgsParserWrapper, self).__init__()

        self.args_parser = args_parser
        self.spec_object = spec_object

    @property
    def argspec(self):
        return self.args_parser.argspec

    def __call__(self, latex_walker, token_reader, parsing_state, **kwargs):

        argsresult = self.args_parser.parse_args(w=latex_walker,
                                                 pos=token_reader.cur_pos(),
                                                 parsing_state=parsing_state)

        logger.debug("Parsed legacy callable args from %s; argsresult = %r",
                     self.args_parser, argsresult)

        if len(argsresult) == 4:
            (nodeargd, apos, alen, adic) = argsresult
        else:
            (nodeargd, apos, alen) = argsresult
            adic = {}

        apos_end = apos + alen
        token_reader.move_to_pos_chars(apos_end)

        nodeargd.pos = apos
        nodeargd.pos_end = apos_end

        new_parsing_state = adic.get('new_parsing_state', None)
        inner_parsing_state = adic.get('inner_parsing_state', None)

        # We can't return parsing_state_delta here, because the carryover info
        # associated with *argument* (and *body*) parsers of a spec are ignored
        # by MacroCallParser's and friends.  Instead, we set an internal
        # attribute on the node, which the spec's overwritten
        # make_after_parsing_state_delta() & make_body_parsing_state_delta()
        # pick up appropriately.

        if new_parsing_state is not None:
            nodeargd._legacy_pyltxenc2_new_parsing_state = new_parsing_state

        if inner_parsing_state is not None:
            nodeargd._legacy_pyltxenc2_inner_parsing_state_delta = inner_parsing_state

        return nodeargd, None


### END_PYLATEXENC2_LEGACY_SUPPORT_CODE
