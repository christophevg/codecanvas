# C.py
# language emitter implementation
# author: Christophe VG

from util.visitor import stacked

import codecanvas.language     as language
import codecanvas.instructions as code
import codecanvas.structure    as structure

from codecanvas.platform import Platform

class Emitter(object):
  def __init__(self, platform=None):
    self.output = None
    self.platform = platform

  def __str__(self): return "C Emitter"

  def output_to(self, output):
    self.output = output
    return self

  def emit(self, code):
    # two phases, two visitations: first to extend the code, next to dump it
    code.accept(Extender())
    if self.output: code.accept(Builder(self.output, platform=self.platform))
    else: return code.accept(Dumper(platform=self.platform))

class Extender(language.Visitor):
  """
  Visitor for CodeCanvas-based ASTs to add code automagically.
  """

  @stacked
  def visit_Print(self, printer):
    """
    When using print(f) we need to include <stdio.h> once per module.
    """
    module = self.stack[1]
    if module.select("dec", "import_stdio") == None:
      module.select("dec").append(code.Import("<stdio.h>")) \
                          .stick_top() \
                          .tag("import_stdio")

  tuple_index = 0
  def visit_TupleType(self, tuple):
    """
    Tuples are structured types.
    """
    # TODO: create nicer names
    name = "tuple_" + str(Extender.tuple_index)
    Extender.tuple_index += 1
    struct = code.StructuredType(name)
    for index, type in enumerate(tuple.types):
      struct.append(code.Property("elem_"+str(index), type))

    unit = self.stack[0]
    if unit.find("tuples") == None:
      unit.append(structure.Module("tuples"))

    unit.find("tuples").select("def").append(struct)

    # replace tuple type by a NamedType
    # TODO: we assume every parent has a .type property that can be replaced!!!
    self.stack[-1].type = code.NamedType(name)

class Generic(Platform):
  def type(self, type):
    return {
      "ByteType"    : "char",
      "BooleanType" : "int",
      "IntegerType" : "int",
      "FloatType"   : "float",
      "LongType"    : "long"
    }[str(type)]

class Dumper(language.Dumper):
  """
  Visitor for CodeCanvas-based ASTs producing actual C code.
  """  
  def __init__(self, platform=None):
    if platform is None: platform = Generic()
    assert isinstance(platform, Platform)
    self.platform = platform

  def visit_Function(self, function):
    return function.type.accept(self) + " " + function.name + \
           "(" + (",".join([param.accept(self) for param in function.params]) \
                   if len(function.params) else "void") + ") " + \
           "{\n" + \
           "\n".join([child.accept(self) for child in function]) + \
           "\n}"

  def visit_Parameter(self, param):
    return param.type.accept(self) + " " + param.id.accept(self)

  # Statements

  def visit_Print(self, printed):
    return "printf(" + printed.string.accept(self) + ");"
  
  def visit_Import(self, importer):
    file = importer.imported
    if not file[0:1] == "<": file = '"' + file + '.h"'
    return "#import " + file

  def visit_IfStatement(self, cond):
    return "if(" + cond.expression.accept(self) + ")" + \
           "{" + "\n".join([stmt.accept(self) for stmt in cond.true_clause]) + "}" + \
           (("else {" + "\n".join([stmt.accept(self) \
                          for stmt in cond.false_clause]) + \
                  "}") if len(cond.false_clause) > 0 else "")

  def visit_CaseStatement(self, case_stmt):
    code = ""
    for case, consequence in zip(case_stmt.cases, case_stmt.consequences):
      code += "case(" + case_stmt.expression.accept(self) + "->" + case.accept(self) + ")" + \
                "{" + \
                  "\n".join([stmt.accept(self) for stmt in consequence]) + \
                "}"
    return code

  def visit_EmptyStatement(self, stmt):
    return ""

  def visit_Assign(self, stmt):
    return stmt.operand.accept(self) + " = " + stmt.expression.accept(self) + ";"

  def visit_Add(self, stmt):
    return stmt.operand.accept(self) + " += " + stmt.expression.accept(self) + ";"

  def visit_Sub(self, stmt):
    return stmt.operand.accept(self) + " -= " + stmt.expression.accept(self) + ";"

  def visit_MethodCall(self, call):
    # TODO: change this into actual C code !!!
    return call.obj.accept(self) + "->" + call.method.name + "(" + \
           ",".join([arg.accept(self) for arg in call.arguments]) +  ")"

  def visit_Object(self, obj):
    return obj.name

  def visit_Inc(self, stmt):
    return stmt.operand.accept(self) + "++;"

  def visit_Dec(self, stmt):
    return stmt.operand.accept(self) + "--;"


  def visit_Plus(self, stmt):
    return "(" + stmt.left.accept(self) + " + " + stmt.right.accept(self) + ")"

  def visit_Minus(self, stmt):
    return "(" + stmt.left.accept(self) + " - " + stmt.right.accept(self) + ")"

  def visit_Mult(self, stmt):
    return "(" + stmt.left.accept(self) + " * " + stmt.right.accept(self) + ")"

  def visit_Div(self, stmt):
    return "(" + stmt.left.accept(self) + " / " + stmt.right.accept(self) + ")"

  # Types

  def visit_NamedType(self, type):
    return type.name

  def visit_VoidType(self, type):
    return "void"

  def visit_FloatType(self, type):
    return self.platform.type(type)

  def visit_IntegerType(self, type):
    return self.platform.type(type)

  def visit_LongType(self, type):
    return self.platform.type(type)

  def visit_BooleanType(self, type):
    return self.platform.type(type)

  def visit_ByteType(self, type):
    return self.platform.type(type)

  def visit_ManyType(self, type):
    return type.type.accept(self) + "*"

  def visit_ObjectType(self, type):
    return type.name

  def visit_TupleType(self, type):
    raise NotImplementedError, "Tuples aren't supported in C. " + \
                               "Extender should have replaced this."

  def visit_StructuredType(self, struct):
    return "typedef struct {\n" + \
           "\n".join([prop.accept(self) for prop in struct]) + \
           "\n} " + struct.name.accept(self) + "_t;"

  def visit_Property(self, prop):
    return prop.type.accept(self) + " " + prop.name.accept(self) + ";"

  # Fragments

  def visit_IntegerLiteral(self, literal):
    return str(literal.value)

  def visit_FloatLiteral(self, literal):
    return str(literal.value)
  
  def visit_StringLiteral(self, string):
    return '"' + string.data.replace("\n", '\\n') + '"'

  def visit_BooleanLiteral(self, bool):
    return "TRUE" if bool.value else "FALSE"

  def visit_Identifier(self, id):
    return id.name

  def visit_ListLiteral(self, literal):
    # TODO: implement this in C !!!
    return ",".join([item.accept(self) for item in literal.children])

  def visit_AtomLiteral(self, literal):
    # TODO: implement this in C !!!
    return "atom_" + literal.name

  def visit_ObjectProperty(self, prop):
    # TODO: implement this in C !!!
    return prop.obj.accept(self) + "->" + prop.prop.accept(self)

  def visit_Comment(self, comment):
    if "\n" in comment.comment:
      return "/* " + comment.comment + " */"
    else:
      return "// " + comment.comment

  # Loops
  
  def visit_WhileDo(self, loop):
    return "while(" + loop.condition.accept(self) + ") {\n" + \
           self.visit_children(loop) + \
           "\n}"

  def visit_RepeatUntil(self, loop):
    return "do {\n" + \
           self.visit_children(loop) + \
           "\n} while(!(" + loop.condition.accept(self) + "));"

  # Calls
  
  def visit_FunctionCall(self, call):
    return call.function.name + "(" + self.visit_children(call, ", ")  + ")"

  def visit_SimpleVariable(self, var):
    return var.id.accept(self)

  # Matching
  
  def visit_Match(self, match):
    # TODO
    return "match(" + match.comp.accept(self) + \
           (("," + match.expression.accept(self)) \
             if not match.expression is None else "") + \
           ")"

  def visit_Comparator(self, comp):
    # TODO
    return comp.operator

  def visit_Anything(self, comp):
    # TODO
    return "*"

  # Expressions
  
  def visit_And(self, op):
    return "(" + op.left.accept(self) + " && " + op.right.accept(self) + ")"

  def visit_Or(self, op):
    return "(" + op.left.accept(self) + " || " + op.right.accept(self) + ")"

  def visit_Equals(self, op):
    return "(" + op.left.accept(self) + " == " + op.right.accept(self) + ")"
    
  def visit_NotEquals(self, op):
    return "(" + op.left.accept(self) + " != " + op.right.accept(self) + ")"
    
  def visit_LT(self, op):
    return "(" + op.left.accept(self) + " < " + op.right.accept(self) + ")"
    
  def visit_LTEQ(self, op):
    return "(" + op.left.accept(self) + " <= " + op.right.accept(self) + ")"

  def visit_GT(self, op):
    return "(" + op.left.accept(self) + " > " + op.right.accept(self) + ")"

  def visit_GTEQ(self, op):
    return "(" + op.left.accept(self) + " >= " + op.right.accept(self) + ")"

  def visit_Modulo(self, op):
    return "(" + op.left.accept(self) + " % " + op.right.accept(self) + ")"

  def visit_Return(self, op):
    return "return;"

  def visit_Not(self, op):
    return "!" + op.operand.accept(self)

  # general purpose child visiting
  def visit_children(self, parent, joiner="\n"):
    return joiner.join([child.accept(self) for child in parent])

class Builder(language.Builder, Dumper):
  """
  Visitor for CodeCanvas-based ASTs producing actual C code, and constructing
  files as needed.
  """
  def __init__(self, output, platform=None):
    language.Builder.__init__(self, output)
    Dumper.__init__(self, platform)

  def ext(self, section):
    return { "def": "h", "dec": "c" }[section]
