# language.py
# interface for language emitters
# author: Christophe VG

import os

from util.visitor import stacked

import codecanvas.instructions as instructions

class Visitor(instructions.Visitor):
  def __init__(self):
    self._stack = []
    self.child  = 0

  def get_stack(self): return self._stack
  stack = property(get_stack)

  def stack_as_string(self):
    return " > ".join([obj.__class__.__name__ for obj in self._stack])

  # visiting functions

  @stacked
  def visit_Unit(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)

  @stacked
  def visit_Section(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)

  @stacked
  def visit_Module(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)

  def visit_Constant(self, code): pass

  @stacked
  def visit_Function(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)

  @stacked
  def visit_Block(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)

  @stacked
  def visit_Print(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)

  @stacked
  def visit_Import(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)
  
  def visit_VoidType(self, code): pass
  def visit_IntegerType(self, code): pass
  def visit_ByteType(self, code): pass
  def visit_FloatType(self, code): pass
  def visit_BooleanType(self, code): pass
  def visit_LongType(self, type): pass
  
  @stacked
  def visit_TupleType(self, code): pass

  @stacked
  def visit_StructuredType(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)

  @stacked
  def visit_Property(self, code):
    code.type.accept(self)
  
  def visit_NamedType(self, code): pass
  
  # loops
  
  @stacked
  def visit_WhileDo(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)

  @stacked
  def visit_RepeatUntil(self, code):
    for index, child in enumerate(code):
      self.child = index
      child.accept(self)
    
  # calls

  @stacked
  def visit_FunctionCall(self, code):
    for index, arg in enumerate(code.arguments):
      self.child = index
      arg.accept(self)

  @stacked
  def visit_MethodCall(self, code):
    code.obj.accept(self)
    code.method.accept(self)
    for index, arg in enumerate(code.arguments):
      self.child = index
      arg.accept(self)


  @stacked
  def visit_SimpleVariable(self, code): pass
  
  # literals
  @stacked
  def visit_BooleanLiteral(self, code): pass

  @stacked
  def visit_Comment(self, code): pass

  @stacked
  def visit_IfStatement(self, cond):
    cond.expression.accept(self)
    for index, stmt in enumerate(cond.true_clause):
      self.child = index
      stmt.accept(self)
    for index, stmt in enumerate(cond.false_clause):
      self.child = index
      stmt.accept(self)

  @stacked
  def visit_CaseStatement(self, case):
    for index, stmt in enumerate(case.cases):
      self.child = index
      stmt.accept(self)
    for consequence in case.consequences:
      for index, stmt in enumerate(consequence):
        self.child = index
        stmt.accept(self)

  @stacked
  def visit_Assign(self, stmt):
    stmt.operand.accept(self)
    stmt.expression.accept(self)

  @stacked
  def visit_Add(self, stmt):
    stmt.operand.accept(self)
    stmt.expression.accept(self)

  @stacked
  def visit_Dec(self, stmt):
    stmt.operand.accept(self)
    stmt.expression.accept(self)

  @stacked
  def visit_Object(self, obj):
    obj.type.accept(self)

  def visit_ObjectType(self, type): pass

  def visit_Identifier(self, id): pass

  @stacked
  def visit_ListLiteral(self, literal):
    for index, child in enumerate(literal):
      self.child = index
      child.accept(self)

  @stacked
  def visit_Inc(self, stmt):
    stmt.operand.accept(self)

  @stacked
  def visit_Dec(self, stmt):
    stmt.operand.accept(self)

  @stacked
  def visit_ManyType(self, type):
    type.type.accept(self)

  def visit_AtomLiteral(self, literal): pass
  def visit_IntegerLiteral(self, literal): pass
  def visit_FloatLiteral(self, literal): pass

  @stacked
  def visit_ObjectProperty(self, prop):
    prop.obj.accept(self)
    prop.prop.accept(self)
    prop.type.accept(self)

  @stacked
  def visit_Not(self, op):
    op.operand.accept(self)

  @stacked
  def visit_And(self, op):       self.visit_BinOp(op)

  @stacked
  def visit_Or(self, op):        self.visit_BinOp(op)

  @stacked
  def visit_Equals(self, op):    self.visit_BinOp(op)

  @stacked
  def visit_NotEquals(self, op): self.visit_BinOp(op)

  @stacked
  def visit_LT(self, op):        self.visit_BinOp(op)

  @stacked
  def visit_LTEQ(self, op):      self.visit_BinOp(op)

  @stacked
  def visit_GT(self, op):        self.visit_BinOp(op)

  @stacked
  def visit_GTEQ(self, op):      self.visit_BinOp(op)

  @stacked
  def visit_Plus(self, op):      self.visit_BinOp(op)

  @stacked
  def visit_Minus(self, op):     self.visit_BinOp(op)

  @stacked
  def visit_Mult(self, op):      self.visit_BinOp(op)

  @stacked
  def visit_Div(self, op):       self.visit_BinOp(op)

  @stacked
  def visit_Modulo(self, op):    self.visit_BinOp(op)

  def visit_BinOp(self, op):
    op.left.accept(self)
    op.right.accept(self)

  @stacked
  def visit_Plus(self, stmt):
    stmt.left.accept(self)
    stmt.right.accept(self)

  @stacked
  def visit_Minus(self, stmt):
    stmt.left.accept(self)
    stmt.right.accept(self)

  @stacked
  def visit_Mult(self, stmt):
    stmt.left.accept(self)
    stmt.right.accept(self)

  @stacked
  def visit_Div(self, stmt):
    stmt.left.accept(self)
    stmt.right.accept(self)

  @stacked
  def visit_Match(self, match):
    match.comp.accept(self)
    if not match.expression is None: match.expression.accept(self)

  def visit_Comparator(self, comp): pass
  def visit_Anything(self, comp): pass

  def visit_Return(self, op): pass

class Dumper(Visitor):
  """
  Base-class for dumpers that simply dump out a CodeCanvas as a string.
  """
  @stacked
  def visit_Unit(self, code):
    return "".join([child.accept(self) for child in code])

  @stacked
  def visit_Module(self, code):
    return "".join([child.accept(self) for child in code])

  @stacked
  def visit_Section(self, code):
    return "\n".join([child.accept(self) for child in code])

class Builder(object):
  """
  Mixin class for overriding default behaviour of a Dumper, allowing it to
  construct output to files.
  """
  def __init__(self, output="output"):
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
