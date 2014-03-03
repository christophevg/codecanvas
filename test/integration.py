# instructions.py
# tests Instruction functionality
# author: Christophe VG

import unittest

from src.codecanvas import Code

import src.instructions as code
import src.languages.C  as C

class TestIntegration(unittest.TestCase):

  def assertEqualToSource(self, tree, source):
    result = C.Emitter().emit(tree)
    if result != source: print result
    self.assertEqual(result, source)

  def test_types(self):
    self.assertEqualToSource(code.VoidType(),    "void" )
    self.assertEqualToSource(code.IntegerType(), "int"  )
    self.assertEqualToSource(code.LongType(),    "long" )
    self.assertEqualToSource(code.FloatType(),   "float")
    self.assertEqualToSource(code.ByteType(),    "char" )
    self.assertEqualToSource(code.BooleanType(), "BOOL" )

  def test_structured_type(self):
    struct = code.StructuredType("something")
    struct.tag("struct_something")

  def test_simple_function(self):
    tree = code.Function("name")
    self.assertEqualToSource(tree, "void name(void) {\n\n}")

  def test_function_with_type(self):
    tree = code.Function("name", type=code.FloatType())
    self.assertEqualToSource(tree, "float name(void) {\n\n}")

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
  unittest.TextTestRunner(verbosity=2).run(suite)
