# structure.py
# tests Structure functionality
# author: Christophe VG

import unittest

from src.structure import Unit, Module, Section

class TestStructure(unittest.TestCase):
  
  def test_unit(self):
    unit = Unit()
    # nothing to test here right now.

  def test_module_name(self):
    module = Module("name")
    self.assertEqual(module.name, "name")

  def test_module_selftagging(self):
    module = Module("name")
    self.assertEqual(len(module.tags), 1)
    self.assertEqual(module.tags[0], "name")

  def test_section_name(self):
    section = Section("name")
    self.assertEqual(section.name, "name")

  def test_section_selftagging(self):
    section = Section("name")
    self.assertEqual(len(section.tags), 1)
    self.assertEqual(section.tags[0], "name")

  def test_module_section_building(self):
    module = Module("name")
    self.assertEqual(len(module.children), 2)
    self.assertIsInstance(module.children[0], Section)
    self.assertIsInstance(module.children[1], Section)
    self.assertEqual(module.children[0].name, "def")
    self.assertEqual(module.children[1].name, "dec")

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestStructure)
  unittest.TextTestRunner(verbosity=2).run(suite)
