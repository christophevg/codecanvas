# language.py
# interface for language emitters
# author: Christophe VG

import os

from util.visitor import stacked

import codecanvas.instructions as instructions

class Visitor(instructions.Visitor):
  def __init__(self):
    self._stack = []

  def get_stack(self): return self._stack
  stack = property(get_stack)

  def stack_as_string(self):
    return " > ".join([obj.__class__.__name__ for obj in self._stack])

  @stacked
  def visit_Unit(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_Section(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_Module(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_Function(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_Block(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_ParameterList(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_Print(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_Import(self, code):
    for child in code: child.accept(self)
  
  def visit_VoidType(self, code): pass
  def visit_IntegerType(self, code): pass
  def visit_ByteType(self, code): pass
  def visit_FloatType(self, code): pass
  def visit_BooleanType(self, code): pass
  def visit_LongType(self, type): pass
  
  @stacked
  def visit_StructuredType(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_Property(self, code): pass
  
  # loops
  
  @stacked
  def visit_WhileDo(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_RepeatUntil(self, code):
    for child in code: child.accept(self)
    
  # calls

  @stacked
  def visit_FunctionCall(self, code):
    for child in code: child.accept(self)

  @stacked
  def visit_SimpleVariable(self, code): pass
  
  # literals
  @stacked
  def visit_BooleanLiteral(self, code): pass

class Dumper(Visitor):
  """
  Base-class for dumpers that simply dump out a CodeCanvas as a string.
  """
  def visit_Unit(self, code):
    return "".join([child.accept(self) for child in code])

  def visit_Module(self, code):
    return "".join([child.accept(self) for child in code])

  def visit_Section(self, code):
    return "\n".join([child.accept(self) for child in code])

class Builder(object):
  """
  Mixin class for overriding default behaviour of a Dumper, allowing it to
  construct output to files.
  """
  def __init__(self, output="out"):
    self.output = output
    self.module = None

  def ext(self, section):
    raise NotImplementedError, "Language.Dumper.ext(self, section)"

  def visit_Unit(self, code):
    for child in code: child.accept(self)

  def visit_Module(self, code):
    self.module = code
    for child in code:
      child.accept(self)
    self.module = None

  def visit_Section(self, code):
    if not os.path.exists(self.output): os.makedirs(self.output)
    file_name = os.path.join(self.output, self.module.name + "." + self.ext(code.name))
    content = "\n".join([child.accept(self) for child in code])
    if not content == "":
      file = open(file_name, 'w+')
      file.write(content + "\n")
      file.close()
