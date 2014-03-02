# instructions.py
# tests Instruction functionality
# author: Christophe VG

import unittest

from src.codecanvas import Code

import src.instructions as code

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
    self.assertEqual(candidate.children, [])    
    
  def test_named_only_function(self):
    f = code.Function("name")
    self.assert_is_code_without_child_modification
    self.assert_has_identifier(f)
    # untyped = VoidType
    self.assertIsInstance(f.type, code.VoidType)
    # children are fixed: params and body
    self.assertEqual(len(f.children), 2)
    self.assertIs(f.children[0], f.params)
    self.assertIs(f.children[1], f.body)
    self.assertIsInstance(f.params, Code)
    self.assertEqual(len(f.params), 0)
    self.assertIsInstance(f.body,   Code)
    self.assertEqual(len(f.body), 0)

  def test_print_without_args(self):
    p = code.Print("hello world")
    self.assert_is_code_without_children(p)

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestInstructions)
  unittest.TextTestRunner(verbosity=2).run(suite)
