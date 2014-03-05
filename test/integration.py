# instructions.py
# tests Instruction functionality
# author: Christophe VG

import unittest

from codecanvas.structure import Unit, Module, Section

import codecanvas.instructions as code
import codecanvas.languages.C  as C

class TestIntegration(unittest.TestCase):

  def setUp(self):
    self.unit = Unit()
    self.unit.append(Module("test"))

  def assertEqualToSource(self, tree, source):
    result   = C.Emitter().emit(tree)
    expected = source.lstrip()
    if result != expected: print result
    self.assertEqual(result, expected)

  def test_types(self):
    self.assertEqualToSource(code.VoidType(),    "void" )
    self.assertEqualToSource(code.IntegerType(), "int"  )
    self.assertEqualToSource(code.LongType(),    "long" )
    self.assertEqualToSource(code.FloatType(),   "float")
    self.assertEqualToSource(code.ByteType(),    "char" )
    self.assertEqualToSource(code.BooleanType(), "BOOL" )

  def test_empty_structured_type(self):
    struct = code.StructuredType("something")
    self.assertEqualToSource(struct, "typedef struct {\n\n} something_t;")

  def test_append_property_to_structured_type(self):
    struct = code.StructuredType("something")
    struct.append(code.Property("prop1", code.FloatType()))
    self.assertEqualToSource(struct, "typedef struct {\nfloat prop1;\n} something_t;")

  def test_structured_type_tagging(self):
    section = Section("test")
    struct  = code.StructuredType("something")
    struct.tag("struct_something")
    section.append(struct)
    section.select("struct_something").append(code.Property("prop1", code.FloatType()))
    self.assertEqualToSource(struct, "typedef struct {\nfloat prop1;\n} something_t;")

  def test_simple_function(self):
    tree = code.Function("name")
    self.assertEqualToSource(tree, "void name(void) {\n\n}")

  def test_function_with_type(self):
    tree = code.Function("name", type=code.FloatType())
    self.assertEqualToSource(tree, "float name(void) {\n\n}")

  def test_while_do_loop(self):
    self.unit.select("test", "dec") \
      .append(code.WhileDo(code.BooleanLiteral(True)) \
        .contains(code.Print("endless"),
                  code.Print("loop")))
    self.assertEqualToSource(self.unit, """
#import <stdio.h>
while(TRUE) {
printf("endless");
printf("loop");
}""")

  def test_repeat_until_loop(self):
    self.unit.select("test", "dec") \
      .append(code.RepeatUntil(code.BooleanLiteral(False)) \
        .contains(code.Print("endless"), code.Print("loop")))
    self.assertEqualToSource(self.unit, """
#import <stdio.h>
do {
printf("endless");
printf("loop");
} while(!(FALSE));""")

  def test_function_call_without_arguments(self):
    self.unit.select("test", "dec") \
      .append(code.FunctionCall("some_func"))
    self.assertEqualToSource(self.unit, "some_func()")

  def test_function_call_with_arguments(self):
    self.unit.select("test", "dec") \
      .append(code.FunctionCall("some_func")) \
      .append(code.SimpleVariable("a"), 
              code.SimpleVariable("b"),
              code.BooleanLiteral(False))
    self.assertEqualToSource(self.unit, "some_func(a, b, FALSE)")

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestIntegration)
  unittest.TextTestRunner(verbosity=2).run(suite)
