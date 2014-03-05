# instructions.py
# tests Instruction functionality
# author: Christophe VG

import unittest

from codecanvas.base import Code

import codecanvas.instructions as code

class TestInstructions(unittest.TestCase):

  def assert_is_code_without_child_modification(self, candidate):
    self.assertIsInstance(candidate, Code)
    self.assertRaises(NotImplementedError, candidate.append)
    self.assertRaises(NotImplementedError, candidate.contains)
    self.assertRaises(NotImplementedError, candidate.insert_before)
    self.assertRaises(NotImplementedError, candidate.insert_after)

  def assert_has_identifier(self, candidate):
    self.assertIsInstance(candidate.id, code.Identifier)

  def assert_is_code_without_children(self, candidate):
    self.assert_is_code_without_child_modification(candidate)
    self.assertRaises(NotImplementedError, lambda: candidate.children)
    
  def test_named_only_function(self):
    f = code.Function("name")
    self.assert_has_identifier(f)
    # untyped = VoidType
    self.assertIsInstance(f.type, code.VoidType)

  def test_print_without_args(self):
    p = code.Print("hello world")
    self.assert_is_code_without_children(p)

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestInstructions)
  unittest.TextTestRunner(verbosity=2).run(suite)
