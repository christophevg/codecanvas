# C.py
# language emitter implementation
# author: Christophe VG

from util.visitor  import stacked
from util.check    import isstring

import codecanvas.language     as language
import codecanvas.instructions as code
import codecanvas.structure    as structure

from codecanvas.platform import Platform

# a few additional Code classes for C-specific things
class RefType(code.Type):
  def __init__(self, type):
    super(RefType, self).__init__({"type":type})
    self.type = type
  def __repr__(self): return "ref to " + str(self.type)

class Deref(code.Variable):
  def __init__(self, pointer):
    self.pointer = pointer

class AddressOf(code.Variable):
  def __init__(self, variable):
    self.variable = variable

class Cast(code.Expression):
  def __init__(self, to, expression):
    self.to         = to
    self.expression = expression

class Emitter(object):
  def __init__(self, platform=None):
    self.output = None
    self.platform = platform

  def __str__(self): return "C Emitter"

  def output_to(self, output):
    self.output = output
    return self

  def emit(self, unit):
    # two phases, two visitations: first to transform the code according to
    # platform and language "limitations", ...
    unit.accept(Transformer())
    # next to dump it to files
    if self.output: unit.accept(Builder(self.output, platform=self.platform))
    else:           return unit.accept(Dumper(platform=self.platform))

class Null(code.Expression): pass

class Transformer(language.Visitor):
  """
  Visitor for CodeCanvas-based ASTs to add/remove code automagically. Allows
  for transforming constructs that are not supported by C into comparative
  solutions that are.
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

  tuples = {}
  tuple_index = 0
  @stacked
  def visit_TupleType(self, tuple):
    """
    Tuples are implemented using structured types.
    """
    try:
      named_type = Transformer.tuples[repr(tuple)]
    except:
      # TODO: create nicer/functional names ;-)
      name = "tuple_" + str(Transformer.tuple_index)
      struct = code.StructuredType(name)
      for index, type in enumerate(tuple.types):
        struct.append(code.Property("elem_"+str(index), type))
      # add a self-referencing pointer for use in linked lists
      struct.append(code.Property("next", RefType(code.NamedType(
                      "struct tuple_" + str(Transformer.tuple_index) + "_t"
                    ))))
      Transformer.tuple_index += 1

      unit = self.stack[0]

      # initialize module
      if unit.find("tuples") == None:
        module = unit.append(structure.Module("tuples"))
        module.select("dec").append(code.Import("tuples"))
        # imports
        module.select("def").append(code.Import("<stdint.h>"))
        module.select("def").append(code.Import("<stdlib.h>"))
        module.select("def").append(code.Import("foo-lib/payload"))
        # required import
        anchor = unit.find("requires-tuples")
        code.Import("tuples").insert_before(anchor)

      # add this tuple
      unit.select("tuples", "def").append(struct)

      # add constructor
      params = []
      for index, type in enumerate(tuple.types):
        params.append(code.Parameter("elem_"+str(index), type))
      constructor = code.Function("make_" + name + "_t", type=RefType(code.NamedType(name+"_t")), params=params)
      unit.select("tuples", "def").append(
        code.Prototype( "make_" + name + "_t",
                        type=RefType(code.NamedType(name+"_t")),
                        params=params)
      )
      constructor.append(
        # tuple_0_t* tuple = malloc(sizeof(tuple_0_t))
        code.Assign(
          code.VariableDecl("tuple", RefType(code.NamedType(name+"_t"))),
          code.FunctionCall("malloc", type=type, arguments=[
            code.FunctionCall("sizeof", type=code.IntegerType(),
                              arguments=[code.SimpleVariable(name+"_t")])
          ]))
      )
      # tuple->elem_0 = elem_0
      # tuple->elem_1 = elem_1
      for index, type in enumerate(tuple.types):
        if isinstance(type, code.ObjectType):
          constructor.append(
            code.Assign(
              code.ObjectProperty("tuple", "elem_" + str(index)),
              code.FunctionCall("copy_" + str(type.name), type=type, arguments=[
                code.SimpleVariable("elem_"+str(index))
              ])
            )
          )
        else:
          constructor.append(
            code.Assign(
              code.ObjectProperty("tuple", "elem_" + str(index)),
              code.SimpleVariable("elem_"+str(index))
            )
          )
      constructor.append(code.Return(code.SimpleVariable("tuple")))
      unit.select("tuples", "dec").append(constructor)

      # add (destructor) free
      params = [code.Parameter("tuple", RefType(code.NamedType(name+"_t")))]
      destructor = code.Function("free_" + name + "_t", params=params)
      unit.select("tuples", "def").append(
        code.Prototype( "free_" + name + "_t", params=params )
      )
      for index, type in enumerate(tuple.types):
        if isinstance(type, code.ObjectType):
          destructor.append(
            code.FunctionCall("free_" + str(type.name), type=code.VoidType(),
              arguments=[
                code.ObjectProperty("tuple", "elem_"+str(index))
              ])
          )
      destructor.append(
        code.FunctionCall("free", arguments=[
          code.SimpleVariable("tuple")
        ])
      )
      unit.select("tuples", "dec").append(destructor)

      # add copy (-constructor)
      params = [code.Parameter("source", RefType(code.NamedType(name+"_t")))]
      copyconstructor = code.Function("copy_" + name + "_t", params=params,
                                       type=RefType(code.NamedType(name+"_t")))
      unit.select("tuples", "def").append(
        code.Prototype("copy_" + name + "_t", params=params,
                       type=RefType(code.NamedType(name+"_t")))
      )
      copyconstructor.append(
        # tuple_0_t* tuple = malloc(sizeof(tuple_0_t))
        code.Assign(
          code.VariableDecl("tuple", RefType(code.NamedType(name+"_t"))),
          code.FunctionCall("malloc", type=type, arguments=[
            code.FunctionCall("sizeof", type=code.IntegerType(),
                              arguments=[code.SimpleVariable(name+"_t")])
          ]))
      )
      for index, type in enumerate(tuple.types):
        if isinstance(type, code.ObjectType):
          copyconstructor.append(
            code.Assign(
              code.ObjectProperty("tuple", "elem_" + str(index)),
              code.FunctionCall("copy_" + str(type.name), type=type, arguments=[
                code.ObjectProperty("source", "elem_"+str(index))
              ])
            )
          )
        else:
          copyconstructor.append(
            code.Assign(
              code.ObjectProperty("tuple", "elem_" + str(index)),
              code.ObjectProperty("source", "elem_"+str(index))
            )
          )
      copyconstructor.append(code.Return(code.SimpleVariable("tuple")))
      unit.select("tuples", "dec").append(copyconstructor)

      named_type = code.NamedType(name+"_t")

    # replace tuple type by a NamedType
    Transformer.tuples[repr(tuple)] = named_type
    return named_type

  @stacked
  def visit_ListLiteral(self, list):
    """
    If one of out items is a ListLiteral, import it, they will be collapsed
    anyway and then we don't have issues with arg counts.
    ISSUE: this is caused by the conversion of Atoms to ListLiterals :-(
    """
    super(Transformer, self).visit_ListLiteral(list)
    
    children = []
    for item in list.children:
      if isinstance(item, code.ListLiteral):
        for subitem in item.children:
          children.append(subitem)
      else:
        children.append(item)
    
    # FIXME: this is too intrusive ;-(
    list.floating = children

  atoms = []
  @stacked
  def visit_AtomLiteral(self, atom):
    """
    Atoms are constructed using two consecutive ByteLiterals. It is assumed that
    atoms will be used primarily in lists that are emitted to variable argument
    list accepting functions.
    """
    # TODO: make this scheme more robust
    try:
      index = Transformer.atoms.index(atom.name) + 1
    except:
      Transformer.atoms.append(atom.name)
      index = len(Transformer.atoms)

    # replace the atom with a ListLiteral of 0x00 and 0x.. <- sequence
    return code.ListLiteral().contains(code.ByteLiteral(0),
                                       code.ByteLiteral(index))

  @stacked
  def visit_Function(self, function):
    """
    1. Prune empty function declarations.
    2. Add declarations in module definition (until public/private support)
    """
    if len(function.children) < 1:
      if len(self.stack) > 1:
        self.stack[-2].remove_child(self.child)
    else:  # 2. add declarations
      module = self.stack[1]
      declaration = function
      module.select("def").append(code.Prototype(function.name, function.type, function.params))
  
    super(Transformer, self).visit_Function(function)

  @stacked
  def visit_MethodCall(self, call):
    """
    MethodCalls are transformed into FunctionCalls. If the object on which the
    method is invoked is ManyType, the prefix is set to "list", else to the name
    of the (Object)Type in plural.
    """
    # first let the standard visitor visit all lower-level dependencies
    super(Transformer, self).visit_MethodCall(call)

    if isinstance(call.obj.type, code.ManyType): return self.visit_ListCall(call)

    # non-list methodcalls are turned into 
    if not isinstance(call.obj.type, code.ObjectType):
      raise NotImplementedError, "only list- and object-types are supported"

    name = call.obj.type.name + "_" + call.method.name
    # create FunctionCall with object as first argument
    function = code.FunctionCall(name, arguments=[call.obj], type=call.type)
    for arg in call.arguments:
      function.arguments.append(arg)

    # replace methodcall by functioncall, by returning it
    return function

  def visit_ListCall(self, call):
    # arguments to the original methodcall can be matchers, those should be 
    # inlined, remaining arguments are normally literals that should be
    # converted to matchers
    # TODO: make this generic ;-(
    matchers  = []
    arguments = []
    for arg in call.arguments:
      if isinstance(arg, code.ListLiteral):
        for subarg in arg:
          if isinstance(subarg, code.ListLiteral):
            for subsubarg in subarg:
              if isinstance(subsubarg, code.Match):
                matchers.append(subsubarg)
              elif isinstance(subsubarg, code.Literal):
                matchers.append(code.Match("==", subsubarg))
              else:
                matchers.append(None)     # placeholder to match argument
                arguments.push(subsubarg)

          else :
            if isinstance(subarg, code.Match):
              matchers.append(subarg)
            elif isinstance(subarg, code.Literal):
              matchers.append(code.Match("==", subarg))
            else:
              matchers.append(None)       # placeholder to match argument
              arguments.append(subarg)
          
      else:
        if isinstance(arg, code.Match):
          matchers.append(arg)
        elif isinstance(arg, code.Literal):
          matchers.append(code.Match("==", arg))
        else:
          matchers.append(None)           # placeholder to match argument
          arguments.append(arg)

    # determine type of list
    type_name = {
      "NamedType" : lambda: call.obj.type.type.name
    }[str(call.obj.type.type.__class__.__name__)]()

    # create list manipulating customized function
    [function, byref] = \
      self.create_list_manipulator(call.obj.type, type_name, call.method.name,
                                   matchers, arguments)

    if byref: obj = AddressOf(call.obj)
    else:     obj = call.obj

    new_arguments = [obj]
    if call.method.name != "remove" and len(arguments) > 0:
      new_arguments.append(
       code.FunctionCall("make_" + type_name, arguments, type=call.obj.type)
      )
    else:
      for arg in arguments:
        new_arguments.append(arg)

    # create FunctionCall with object as first argument
    # and replace methodcall by functioncall
    return code.FunctionCall(function.name, new_arguments, type=function.type)

  def create_list_manipulator(self, type, type_name, method, matchers, arguments):
    """
    Dispatcher for the creation of list-manipulating functions.
    """
    self.prepare_lists_module()
    return {
      "contains": self.create_list_contains,
      "push"    : self.create_list_push,
      "remove"  : self.create_list_remove
    }[method](type, type_name, matchers, arguments)

  def prepare_lists_module(self):
    unit = self.stack[0]
    # make sure that the listing module exists, else create it
    if unit.find("lists") == None:
      module = unit.append(structure.Module("lists"))
      module.select("dec").append(code.Import("lists"))
      module.select("def").append(code.Import("<stdlib.h>"))
      module.select("def").append(code.Import("tuples"))
      module.select("def").append(code.Import("foo-lib/time"))
      # add to includes
      unit.select("includes", "def").append(code.Import("lists"))

  def create_list_contains(self, type, type_name, matchers, arguments):
    name     = "list_of_" + type_name + "s_contains"
    function = self.stack[0].find(name)
    if not function is None: return function

    params = [ code.Parameter("iter", type) ]

    # construct loop body
    body = code.WhileDo(code.NotEquals(code.SimpleVariable("iter"), Null()))

    # turn matchers into list of conditions
    [condition, suffix] = self.transform_matchers_into_condition(matchers, arguments)
    name += suffix
    body.append(code.IfStatement(condition,
                  [ code.Return(code.BooleanLiteral(True)) ]
                ),
                code.Assign("iter",
                            code.ObjectProperty("iter", "next"))
    )
    # provide a prototype
    self.stack[0].find("lists").select("def").append(
      code.Prototype(name, type=code.BooleanType(), params=params)
    )
    # create function and return it
    return (self.stack[0].find("lists").select("dec").append(
      code.Function(name, type=code.BooleanType(), params=params)
          .contains(body,
                    code.Return(code.BooleanLiteral(False))
          ).tag(name)
    ), False)

  def create_list_push(self, type, type_name, matchers, arguments):
    name     = "list_of_" + type_name + "s_push"
    function = self.stack[0].find(name)
    if not function is None: return function
    
    # pushing accepts the type of the list's content as parameter(d)
    params = [ code.Parameter("list", RefType(type)),
               code.Parameter("item", RefType(type.type))
             ]

    # provide a prototype
    self.stack[0].find("lists").select("def").append(
      code.Prototype(name, type=code.VoidType(), params=params)
    )
    return (self.stack[0].find("lists").select("dec").append(
      code.Function(name, type=code.VoidType(), params=params)
          .contains(
            code.Assign(code.ObjectProperty("item", "next"),
                        Deref(code.SimpleVariable("list"))),
            code.Assign(Deref(code.SimpleVariable("list")),
                        code.SimpleVariable("item"))
          ).tag(name)
    ), True)

  def create_list_remove(self, type, type_name, matchers, arguments):
    name   = "list_of_" + type_name + "s_remove"
    function = self.stack[0].find(name)
    if not function is None: return function

    params = [ code.Parameter("list", RefType(type)) ]

    # TODO: this should have been moved up and the info was a hack anyway :-(
    args = 0
    for arg in arguments:
      params.append(
        code.Parameter(
          "arg_"+str(args),
          code.ObjectType(arg.info.name)
        )
      )
      args += 1

    # turn matchers into list of conditions
    [condition, suffix] = self.transform_matchers_into_condition(matchers, arguments)
    name += suffix

    # construct body
    body = code.WhileDo(code.NotEquals(code.SimpleVariable("iter"), Null())) \
               .contains(
                 code.IfStatement(condition, [
                   code.IfStatement(code.Equals(code.SimpleVariable("prev"),
                                                Null()),
                     [ code.Assign(Deref(code.SimpleVariable("list")),
                                   code.ObjectProperty("iter", "next")) ],
                     [ code.Assign(code.ObjectProperty("prev", "next"),
                                   code.ObjectProperty("iter", "next")) ]
                   ),
                   code.FunctionCall("free_"+type_name,
                                    [ code.SimpleVariable("iter") ]),
                   code.Inc(code.SimpleVariable("removed"))
                 ]),
                 code.Assign(code.SimpleVariable("prev"),
                             code.SimpleVariable("iter")),
                 code.Assign(code.SimpleVariable("iter"),
                             code.ObjectProperty("iter", "next"))
               )
  
    # provide a prototype
    self.stack[0].find("lists").select("def").append(
      code.Prototype(name, type=code.IntegerType(), params=params)
    )
    # create function and return it
    return (self.stack[0].find("lists").select("dec").append(
      code.Function(name, type=code.IntegerType(), params=params)
          .contains(code.Assign(code.VariableDecl("removed", code.IntegerType()),
                                code.IntegerLiteral(0)),
                    code.Assign(code.VariableDecl("iter", RefType(type.type)),
                                Deref(code.SimpleVariable("list"))),
                    code.Assign(code.VariableDecl("prev", RefType(type.type)),
                                Null()),
                    body,
                    code.Return(code.SimpleVariable("removed"))
          )
    ), True)

  def transform_matchers_into_condition(self, matchers, arguments):
    suffix = ""
    conditions = []
    args = 0
    for idx, matcher in enumerate(matchers):
      if matcher == None:
        arg_type = arguments[args].info.name
        suffix += "_match_arg_" + str(args)
        conditions.append(
          code.FunctionCall("equal_"+arg_type, type=code.BooleanType(),
            arguments=[
              code.SimpleVariable("arg_"+str(args)),
              code.ObjectProperty("iter", "elem_" + str(idx)),
            ]
          )
        )
        args += 1
      elif not isinstance(matcher, code.Anything) and matcher.comp.operator != "*":
        suffix += "_match_" + matcher.as_label()
        conditions.append( {
          "<"  : code.LT,
          ">"  : code.GT,
          "<=" : code.LTEQ,
          ">=" : code.GTEQ,
          "==" : code.Equals,
          "!=" : code.NotEquals
        }[matcher.comp.operator](code.ObjectProperty("iter", "elem_"+str(idx)),
                                 matcher.expression)
        )
    # join conditions together with AND (TODO: should have factory method)
    if len(conditions) < 1:
      conditions = code.BooleanLiteral(True)
    elif len(conditions) < 2:
      conditions = conditions.pop(0)
    else:
      test = code.And(conditions.pop(0), conditions.pop(0))
      while len(conditions) > 0:
        test = code.And(test, conditions.pop(0))
      conditions = test
    
    return (conditions, suffix)

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
    super(Dumper, self).__init__()
    if platform is None: platform = Generic()
    assert isinstance(platform, Platform)
    self.platform = platform

  @stacked
  def visit_Constant(self, constant):
    return "#define " + constant.id.accept(self) + " " + constant.value.accept(self)

  @stacked
  def visit_Function(self, function):
    return function.type.accept(self) + " " + function.name + \
           "(" + (", ".join([param.accept(self) for param in function.params]) \
                   if len(function.params) else "void") + ") " + \
           "{\n" + \
           "\n".join([child.accept(self) for child in function]) + \
           "\n}"

  @stacked
  def visit_Prototype(self, function):
    return function.type.accept(self) + " " + function.name + \
           "(" + (", ".join([param.accept(self) for param in function.params]) \
                   if len(function.params) else "void") + ");"

  @stacked
  def visit_Parameter(self, param):
    return param.type.accept(self) + " " + param.id.accept(self)

  # Statements

  @stacked
  def visit_Print(self, printed):
    return "printf(" + printed.string.accept(self) + ");"
  
  @stacked
  def visit_Import(self, importer):
    file = importer.imported
    if file[-2:] == ".c": file = '"' + file + '"'
    else:
      if not file[0:1] == "<": file = '"' + file + '.h"'
    return "#include " + file

  @stacked
  def visit_IfStatement(self, cond):
    return "if(" + cond.expression.accept(self) + ")" + \
           "{" + "\n".join([stmt.accept(self) for stmt in cond.true_clause]) + "}" + \
           (("else {" + "\n".join([stmt.accept(self) \
                          for stmt in cond.false_clause]) + \
                  "}") if len(cond.false_clause) > 0 else "")

  @stacked
  def visit_ShiftLeft(self, exp):
    return exp.var.accept(self) + " >> " + str(exp.amount);

  @stacked
  def visit_Assign(self, stmt):
    return stmt.operand.accept(self) + " = " + stmt.expression.accept(self) + ";"

  @stacked
  def visit_Add(self, stmt):
    return stmt.operand.accept(self) + " += " + stmt.expression.accept(self) + ";"

  @stacked
  def visit_Sub(self, stmt):
    return stmt.operand.accept(self) + " -= " + stmt.expression.accept(self) + ";"

  @stacked
  def visit_Object(self, obj):
    return obj.name

  @stacked
  def visit_Inc(self, stmt):
    return stmt.operand.accept(self) + "++;"

  @stacked
  def visit_Dec(self, stmt):
    return stmt.operand.accept(self) + "--;"


  @stacked
  def visit_Plus(self, stmt):
    return "(" + stmt.left.accept(self) + " + " + stmt.right.accept(self) + ")"

  @stacked
  def visit_Minus(self, stmt):
    return "(" + stmt.left.accept(self) + " - " + stmt.right.accept(self) + ")"

  @stacked
  def visit_Mult(self, stmt):
    return "(" + stmt.left.accept(self) + " * " + stmt.right.accept(self) + ")"

  @stacked
  def visit_Div(self, stmt):
    return "(" + stmt.left.accept(self) + " / " + stmt.right.accept(self) + ")"

  # Types

  @stacked
  def visit_NamedType(self, type):
    return self.platform.type(type.name)

  @stacked
  def visit_VoidType(self, type):
    return "void"

  @stacked
  def visit_FloatType(self, type):
    return self.platform.type(type)

  @stacked
  def visit_IntegerType(self, type):
    return self.platform.type(type)

  @stacked
  def visit_LongType(self, type):
    return self.platform.type(type)

  @stacked
  def visit_BooleanType(self, type):
    return self.platform.type(type)

  @stacked
  def visit_ByteType(self, type):
    return self.platform.type(type)

  @stacked
  def visit_ManyType(self, type):
    return type.type.accept(self) + "*"

  @stacked
  def visit_AmountType(self, type):
    return type.type.accept(self)

  @stacked
  def visit_ObjectType(self, type):
    name = type.name
    if name[-1] == "s": name = name[0:-1]
    return name + "_t*"

  @stacked
  def visit_StructuredType(self, struct):
    name = struct.name.accept(self)
    if name[-1] == "s": name = name[0:-1] # strip off trailing s from types
    struct_name = name + "_t"
    return "typedef struct " + struct_name + " {\n" + \
           "\n".join([prop.accept(self) for prop in struct]) + \
           "\n} " + struct_name + ";"

  @stacked
  def visit_UnionType(self, struct):
    return "union { " + (" ".join([prop.accept(self) for prop in struct])) + "}"

  @stacked
  def visit_Property(self, prop):
    return prop.type.accept(self) + " " + prop.name.accept(self) + \
      ("" if not isinstance(prop.type, code.AmountType) else "[" + str(prop.type.size) +"]") + \
      ";"

  # Fragments

  @stacked
  def visit_ByteLiteral(self, literal):
    return "0x%02x" % literal.value

  @stacked
  def visit_IntegerLiteral(self, literal):
    return str(literal.value)

  @stacked
  def visit_FloatLiteral(self, literal):
    return str(literal.value)
  
  @stacked
  def visit_StringLiteral(self, string):
    return '"' + string.data.replace("\n", '\\n') + '"'

  @stacked
  def visit_BooleanLiteral(self, bool):
    return "TRUE" if bool.value else "FALSE"

  @stacked
  def visit_Identifier(self, id):
    return id.name

  @stacked
  def visit_ListLiteral(self, literal):
    if len(literal.children) > 0 :
      # strategy: listliterals are passes as varargs, with the number of args as
      # a first argument
      return str(len(literal.children)) + ", " + \
             ", ".join([item.accept(self) for item in literal.children])
    else:
      return "NULL"

  @stacked
  def visit_ObjectProperty(self, prop):
    return prop.obj.accept(self) + "->" + prop.prop.accept(self)

  @stacked
  def visit_StructProperty(self, prop):
    return prop.obj.accept(self) + "." + prop.prop.accept(self)

  @stacked
  def visit_Comment(self, comment):
    if "\n" in comment.comment:
      return "/*\n  " + "\n  ".join(comment.comment.split("\n")) + "\n*/"
    else:
      return "// " + comment.comment

  # Loops
  
  @stacked
  def visit_WhileDo(self, loop):
    return "while(" + loop.condition.accept(self) + ") {\n" + \
           self.visit_children(loop) + \
           "\n}"

  @stacked
  def visit_RepeatUntil(self, loop):
    return "do {\n" + \
           self.visit_children(loop) + \
           "\n} while(!(" + loop.condition.accept(self) + "));"

  # Calls
  
  @stacked
  def visit_FunctionCall(self, call):
    return call.function.name + "(" + \
           ", ".join([arg.accept(self) for arg in call.arguments])  + ")" + \
           (";" if isinstance(call.type, code.VoidType) \
                or isinstance(self.stack[-2], code.Function) else "")

  @stacked
  def visit_SimpleVariable(self, var):
    return var.id.accept(self)

  @stacked
  def visit_ListVariable(self, var):
    return var.id.accept(self) + "[" + str(var.index) + "]"

  # Expressions
  
  @stacked
  def visit_And(self, op):
    return "(" + op.left.accept(self) + " && " + op.right.accept(self) + ")"

  @stacked
  def visit_Or(self, op):
    return "(" + op.left.accept(self) + " || " + op.right.accept(self) + ")"

  @stacked
  def visit_Equals(self, op):
    return "(" + op.left.accept(self) + " == " + op.right.accept(self) + ")"
    
  @stacked
  def visit_NotEquals(self, op):
    return "(" + op.left.accept(self) + " != " + op.right.accept(self) + ")"
    
  @stacked
  def visit_LT(self, op):
    return "(" + op.left.accept(self) + " < " + op.right.accept(self) + ")"
    
  @stacked
  def visit_LTEQ(self, op):
    return "(" + op.left.accept(self) + " <= " + op.right.accept(self) + ")"

  @stacked
  def visit_GT(self, op):
    return "(" + op.left.accept(self) + " > " + op.right.accept(self) + ")"

  @stacked
  def visit_GTEQ(self, op):
    return "(" + op.left.accept(self) + " >= " + op.right.accept(self) + ")"

  @stacked
  def visit_Modulo(self, op):
    return "(" + op.left.accept(self) + " % " + op.right.accept(self) + ")"

  @stacked
  def visit_Return(self, op):
    return "return" + (" " + op.expression.accept(self) if not op.expression is None
                        else "") + ";"

  @stacked
  def visit_Not(self, op):
    return "!" + op.operand.accept(self)

  # C-specific extensions
  @stacked
  def visit_RefType(self, ref):
    return ref.type.accept(self) + "*"

  @stacked
  def visit_VariableDecl(self, decl):
    type_quantifier = ""
    var_quantifier  = ""
    inside_assign = isinstance(self.stack[-2], code.Assign)
    if isinstance(decl.type, code.AmountType):
      if inside_assign: type_quantifier = "*"
      else:             var_quantifier = "[" + str(decl.type.size) +"]"
    return decl.type.accept(self) + type_quantifier + " " + \
           decl.name + var_quantifier + \
      ("" if inside_assign else ";")
      # a bit specific, but for now it seems the only real possibility

  @stacked
  def visit_Deref(self, ref):
    return "*" + ref.pointer.accept(self)

  @stacked
  def visit_Cast(self, cast):
    return "(" + cast.to.accept(self) + ")" + cast.expression.accept(self)

  @stacked
  def visit_Null(self, null):
    return "NULL"

  @stacked
  def visit_AddressOf(self, address):
    return "&" + address.variable.accept(self)

  # general purpose child visiting
  def visit_children(self, parent, joiner="\n"):
    return joiner.join([child.accept(self) for child in parent])

  # unsupported code-constructs for C
  
  def visit_AtomLiteral(self, literal):
    raise NotImplementedError, "Atoms aren't supported in C. " + \
                               "Transformers should have replaced this."

  def visit_TupleType(self, type):
    raise NotImplementedError, "Tuples aren't supported in C. " + \
                               "Transformers should have replaced this."

  def visit_CaseStatement(self, case_stmt):
    raise NotImplementedError, "Case constructs aren't supported in C. " + \
                               "Transformers should have replaced this."

  def visit_Match(self, match):
    raise NotImplementedError, "Matching aren't supported in C. " + \
                               "Transformers should have replaced this."

  def visit_Comparator(self, comp):
    raise NotImplementedError, "Comparators aren't supported in C. " + \
                               "Transformers should have replaced this."

  def visit_Anything(self, comp):
    raise NotImplementedError, "Anything comparator isn't supported in C. " + \
                               "Transformers should have replaced this."

  def visit_MethodCall(self, call):
    raise NotImplementedError, "MethodCalls aren't supported in C. " + \
                               "Transformers should have replaced this."

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

  def transform_Section(self, code, content):
    if code.name == "def":
      content = "#ifndef __" + self.module.name.replace("-", "_").upper() + "_H\n" + \
                "#define __" + self.module.name.replace("-", "_").upper() + "_H\n\n" + \
                content + \
                "\n\n#endif\n"
    return content
