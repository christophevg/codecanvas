# C.py
# language emitter implementation
# author: Christophe VG

from util.visitor import stacked

from .. import language
from .. import instructions as code

class Emitter(object):
  def __init__(self):
    self.output = None

  def __str__(self): return "C Emitter"

  def output_to(self, output):
    self.output = output
    return self

  def emit(self, code):
    # two phases, two visitations: first to extend the code, next to dump it
    code.accept(Extender())
    if self.output: code.accept(Builder(self.output))
    else: return code.accept(Dumper())

class Extender(language.Visitor):
  """
  Visitor for CodeCanvas-based ASTs to add code automagically.
  """

  @stacked
  def visit_Print(self, printer):
    module = self.stack[1]
    if module.select("dec", "import_stdio") == None:
      module.select("dec").append(code.Import("<stdio.h>")) \
                          .stick_top() \
                          .tag("import_stdio") \

class Dumper(language.Dumper):
  """
  Visitor for CodeCanvas-based ASTs producing actual C code.
  """  
  def visit_Function(self, function):
    return function.type.accept(self) + " " + function.name + \
           function.params.accept(self) + " " +  "{\n" + \
           "\n".join([child.accept(self) for child in function]) + \
           "\n}"

  def visit_ParameterList(self, params):
    return "(" + \
           (", ".join([p.type.accept(self) for p in params.parameters]) \
             if len(params.parameters) > 0 else "void") + \
           ")"

  # Statements

  def visit_Print(self, printed):
    return "printf(" + printed.string.accept(self) + ");"
  
  def visit_Import(self, importer):
    return "#import " + importer.imported

  # Types
  # TODO: reintroduce platform

  def visit_NamedType(self, type):
    return type.name

  def visit_VoidType(self, type):
    return "void"

  def visit_FloatType(self, type):
    return "float"

  def visit_IntegerType(self, type):
    return "int"

  def visit_LongType(self, type):
    return "long"

  def visit_BooleanType(self, type):
    return "BOOL"

  def visit_ByteType(self, type):
    return "char"

  def visit_StructuredType(self, struct):
    return "typedef struct {\n" + \
           "\n".join([prop.accept(self) for prop in struct]) + \
           "\n} " + struct.name.accept(self) + "_t;"

  def visit_Property(self, prop):
    return prop.type.accept(self) + " " + prop.name.accept(self) + ";"

  # Fragments
  
  def visit_StringLiteral(self, string):
    return '"' + string.data.replace("\n", '\\n') + '"'

  def visit_BooleanLiteral(self, bool):
    return "TRUE" if bool.value else "FALSE"

  def visit_Identifier(self, id):
    return id.name

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

  # general purpose child visiting
  def visit_children(self, parent, joiner="\n"):
    return joiner.join([child.accept(self) for child in parent])

class Builder(language.Builder, Dumper):
  """
  Visitor for CodeCanvas-based ASTs producing actual C code, and constructing
  files as needed.
  """
  def ext(self, section):
    return { "def": "h", "dec": "c" }[section]
