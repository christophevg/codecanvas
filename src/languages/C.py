# C.py
# language emitter implementation
# author: Christophe VG

from util.visitor import stacked

from .. import language
from .. import instructions as code

class Emitter(object):
  def __init__(self):
    self.output = None

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
           function.params.accept(self) + " " + function.body.accept(self)

  def visit_ParameterList(self, params):
    return "(" + \
           (", ".join([p.type.accept(self) for p in params.parameters]) \
             if len(params.parameters) > 0 else "void") + \
           ")"

  # Statements

  def visit_BlockStmt(self, block):
    return "{\n" + \
           "\n".join([child.accept(self) for child in block.children]) + \
           "\n}"

  def visit_Print(self, printed):
    return "printf(" + printed.string.accept(self) + ");"
  
  def visit_Import(self, importer):
    return "#import " + importer.imported

  # Types

  def visit_VoidType(self, type):
    return "void"

  # Fragments
  
  def visit_StringLiteral(self, string):
    return '"' + string.data.replace("\n", '\\n') + '"'

  def visit_Identifier(self, id):
    return id.name

class Builder(language.Builder, Dumper):
  """
  Visitor for CodeCanvas-based ASTs producing actual C code, and constructing
  files as needed.
  """
  def ext(self, section):
    return { "def": "h", "dec": "c" }[section]
