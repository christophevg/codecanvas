# all.py
# author: Christophe VG

# all unit tests for the CodeCanvas

import unittest

from test.base         import TestBase
from test.examples     import TestExamples

from test.structure    import TestStructure
from test.instructions import TestInstructions
from test.integration  import TestIntegration

if __name__ == '__main__':
  tests = [ unittest.TestLoader().loadTestsFromTestCase(test)
            for test in [ 
                          TestBase,
                          TestExamples,
                          TestStructure,
                          TestInstructions,
                          TestIntegration
                         ]
          ]

  all_tests = unittest.TestSuite( tests )
  unittest.TextTestRunner(verbosity=1).run(all_tests)
