# all.py
# author: Christophe VG

# all unit tests for the CodeCanvas

import unittest

from test.code         import TestCodeCanvas
from test.examples     import TestExamples

from test.structure    import TestStructure
from test.instructions import TestInstructions

if __name__ == '__main__':
  tests = [ unittest.TestLoader().loadTestsFromTestCase(test)
            for test in [ 
                          TestCodeCanvas,
                          TestExamples,
                          TestStructure,
                          TestInstructions
                         ]
          ]

  all_tests = unittest.TestSuite( tests )
  unittest.TextTestRunner(verbosity=1).run(all_tests)
