import unittest
import sys
import logging
logger = logging.getLogger(__name__)

from pylatexenc.macrospec._latexcontextdb import (
    LatexContextDb,
    _autogen_category_prefix
)

from pylatexenc.macrospec import (
    MacroSpec,
    EnvironmentSpec,
    SpecialsSpec,
)



class TestLatexContextDb(unittest.TestCase):


    # TODO........ need more tests here



    def test_extended_with(self):

        context = LatexContextDb()
        context.add_context_category(
            'base-category',
            macros=[ MacroSpec('base', '{'), ],
            environments=[ EnvironmentSpec('baseenv', '{'), ],
            specials=[ SpecialsSpec('~'), ],
        )
        context.freeze()

        logger.debug("context's category list = %r", context.category_list)
        logger.debug("context's d = %r", context.d)
        logger.debug("context's lookup maps are = %r", context.lookup_chain_maps)

        extd1 = dict(
            macros=[ MacroSpec('more', '{'), ],
            environments=[ EnvironmentSpec('moreenv', '{'), ],
            specials=[ SpecialsSpec('!'), ],
        )
        context2 = context.extended_with(**extd1)
    
        logger.debug("context2's category list = %r", context2.category_list)
        logger.debug("context2's d = %r", context2.d)
        logger.debug("context2's lookup maps are = %r", context2.lookup_chain_maps)

        self.assertEqual(len(context2.category_list), 2)
        self.assertTrue(context2.category_list[0].startswith(_autogen_category_prefix))

        self.assertEqual(context2.get_macro_spec('base'),
                         context.get_macro_spec('base'))
        self.assertEqual(context2.get_environment_spec('baseenv'),
                         context.get_environment_spec('baseenv'))
        self.assertEqual(context2.get_specials_spec('~'),
                         context.get_specials_spec('~'))
        self.assertEqual(context2.test_for_specials('~~~~~~~', pos=0),
                         context.get_specials_spec('~'))
        self.assertEqual(context2.get_macro_spec('more'), extd1['macros'][0])
        self.assertEqual(context2.get_environment_spec('moreenv'), extd1['environments'][0])
        self.assertEqual(context2.get_specials_spec('!'), extd1['specials'][0])
        self.assertEqual(context2.test_for_specials('!!!!!', pos=0), extd1['specials'][0])

        extd2 = dict(
            macros=[ MacroSpec('evenmore', '{'), ],
            environments=[ EnvironmentSpec('baseenv', '{'), ], # override baseenv
            specials=[ SpecialsSpec('!!'), ],
        )
        context3 = context2.extended_with(**extd2)
   
        # extended_with() a second time shouldn't add a new category as the
        # first category is already an autogenerated one
        self.assertEqual(len(context3.category_list), 2)
        self.assertEqual(context3.category_list, context2.category_list)
        self.assertTrue(context3.category_list[0].startswith(_autogen_category_prefix))

        logger.debug("context3's category list = %r", context3.category_list)
        logger.debug("context3's d = %r", context3.d)
        logger.debug("context3's lookup maps are = %r", context3.lookup_chain_maps)

        self.assertEqual(context3.get_macro_spec('base'),
                         context.get_macro_spec('base'))
        # self.assertEqual(context3.get_environment_spec('baseenv'),
        #                  context.get_environment_spec('baseenv')) # NO!
        self.assertEqual(context3.get_specials_spec('~'),
                         context.get_specials_spec('~'))
        self.assertEqual(context3.test_for_specials('~~~~~~~', pos=0),
                         context.get_specials_spec('~'))
        self.assertEqual(context3.get_macro_spec('more'), extd1['macros'][0])
        self.assertEqual(context3.get_macro_spec('evenmore'), extd2['macros'][0])
        self.assertEqual(context3.get_environment_spec('moreenv'), extd1['environments'][0])
        self.assertEqual(context3.get_environment_spec('baseenv'), extd2['environments'][0])
        self.assertEqual(context3.get_specials_spec('!'), extd1['specials'][0])
        self.assertEqual(context3.get_specials_spec('!!'), extd2['specials'][0])
        self.assertEqual(context3.test_for_specials('!!!!!', pos=0), extd2['specials'][0])





# ---

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
#
