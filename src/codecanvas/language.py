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

  def accept(self, target):
    """
    General purpose accept handler. Returns an update if the handler provides
    one, else it returns the original value.
    Classic: something.accept(self)
    Now:     something = self.accept(something)
    """
    update = target.accept(self)
    return update if not update is None else target

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
      update = self.accept(child)
      try: code.update_child(code.children.index(child), update)
      except: pass    # index(child) fails when child is no longer in the list

  @stacked
  def visit_Prototype(self, code): pass

  @stacked
  def visit_Block(self, code):
    for index, child in enumerate(code):
      self.child = index
      code.update_child(index, self.accept(child))

  @stacked
  def visit_Print(self, code):
    for index, child in enumerate(code):
      self.child = index
      code.update_child(index, self.accept(child))

  @stacked
  def visit_Import(self, code):
    for index, child in enumerate(code):
      self.child = index
      code.update_child(index, self.accept(child))
  
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
      code.update_child(index, self.accept(child))

  @stacked
  def visit_Property(self, code):
    code.type = self.accept(code.type)
  
  def visit_NamedType(self, code): pass
  
  # loops
  
  @stacked
  def visit_WhileDo(self, code):
    for index, child in enumerate(code):
      self.child = index
      code.update_child(index, self.accept(child))

  @stacked
  def visit_RepeatUntil(self, code):
    for index, child in enumerate(code):
      self.child = index
      code.update_child(index, self.accept(child))
    
  # calls

  @stacked
  def visit_FunctionCall(self, code):
    for index, arg in enumerate(code.arguments):
      self.child = index
      code.arguments[index] = self.accept(arg)

  @stacked
  def visit_MethodCall(self, code):
    code.obj    = self.accept(code.obj)
    code.method = self.accept(code.method)
    for index, arg in enumerate(code.arguments):
      self.child = index
      code.arguments[index] = self.accept(arg)

  @stacked
  def visit_SimpleVariable(self, code): pass

  @stacked
  def visit_ListVariable(self, code): pass
  
  # literals
  @stacked
  def visit_BooleanLiteral(self, code): pass

  @stacked
  def visit_Comment(self, code): pass

  @stacked
  def visit_IfStatement(self, cond):
    cond.expression = self.accept(cond.expression)
    for index, stmt in enumerate(cond.true_clause):
      self.child = index
      cond.true_clause[index] = self.accept(stmt)
    for index, stmt in enumerate(cond.false_clause):
      self.child = index
      cond.false_clause[index] = self.accept(stmt)

  @stacked
  def visit_CaseStatement(self, case):
    for index, stmt in enumerate(case.cases):
      self.child = index
      case.cases[index] = self.accept(stmt)
    for consequence in case.consequences:
      for index, stmt in enumerate(consequence):
        self.child = index
        consequence[index] = self.accept(stmt)

  @stacked
  def visit_Assign(self, stmt):  self.visit_VarExpOp(stmt)

  @stacked
  def visit_Add(self, stmt):     self.visit_VarExpOp(stmt)

  @stacked
  def visit_Dec(self, stmt):     self.visit_VarExpOp(stmt)

  def visit_VarExpOp(self, stmt):
    stmt.operand    = self.accept(stmt.operand)
    stmt.expression = self.accept(stmt.expression)

  @stacked
  def visit_Object(self, obj):
    obj.type = self.accept(obj.type)

  def visit_ObjectType(self, type): pass

  def visit_Identifier(self, id): pass

  @stacked
  def visit_ListLiteral(self, literal):
    for index, child in enumerate(literal):
      self.child = index
      literal.update_child(index, self.accept(child))

  @stacked
  def visit_Inc(self, stmt):
    stmt.operand = self.accept(stmt.operand)

  @stacked
  def visit_Dec(self, stmt):
    stmt.operand = self.accept(stmt.operand)

  @stacked
  def visit_ManyType(self, type):
    type.type = self.accept(type.type)

  @stacked
  def visit_AmountType(self, type):
    type.type = self.accept(type.type)

  @stacked
  def visit_UnionType(self, code):
    for index, child in enumerate(code):
      self.child = index
      code.update_child(index, self.accept(child))

  def visit_AtomLiteral(self, literal): pass
  def visit_IntegerLiteral(self, literal): pass
  def visit_FloatLiteral(self, literal): pass

  @stacked
  def visit_ObjectProperty(self, prop):
    prop.obj  = self.accept(prop.obj)
    prop.prop = self.accept(prop.prop)
    prop.type = self.accept(prop.type)

  @stacked
  def visit_StructProperty(self, prop):
    prop.obj  = self.accept(prop.obj)
    prop.prop = self.accept(prop.prop)

  @stacked
  def visit_Not(self, op):
    op.operand = self.accept(op.operand)

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

  @stacked
  def visit_Plus(self, op):      self.visit_BinOp(op)

  @stacked
  def visit_Minus(self, op):     self.visit_BinOp(op)

  @stacked
  def visit_Mult(self, op):      self.visit_BinOp(op)

  @stacked
  def visit_Div(self, op):       self.visit_BinOp(op)

  def visit_BinOp(self, op):
    op.left  = self.accept(op.left)
    op.right = self.accept(op.right)

  @stacked
  def visit_Match(self, match):
    match.comp = self.accept(match.comp)
    if not match.expression is None:
      match.expression = self.accept(match.expression)

  def visit_Comparator(self, comp): pass
  def visit_Anything(self, comp): pass

  def visit_Return(self, op): pass
  
  def visit_VariableDecl(self, var):
    var.id.accept(self)
    var.type.accept(self)

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
  Mixin class for overriding default behavior of a Dumper, allowing it to
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
      content = self.transform_Section(code, content)
      file = open(file_name, 'w+')
      file.write(content + "\n")
      file.close()

  def transform_Section(self, code, content):
    return content
