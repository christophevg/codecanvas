# instructions.py
# abstract instruction set, implemented as Code
# author: Christophe VG

from util.check   import isstring, isidentifier
from util.visitor import visits

from codecanvas import Code, WithoutChildren, WithoutChildModification, List

# Mixins

class Identified(object):
  def get_name(self): return self.id.name
  name = property(get_name)

# Fragments - are instructions that aren't Codes by itself, but can be visited

class Fragment(object):
  def accept(self, visitor):
    try: return getattr(visitor, "visit_" + self.__class__.__name__)(self)
    except AttributeError: pass
    return ""

class Identifier(Fragment):
  def __init__(self, name):
    assert isidentifier(name), "Not an Identifier: " + name
    self.name = name
  def __repr__(self): return self.name

# Declarations

class Function(Identified, WithoutChildModification, Code):
  def __init__(self, name, type=None, params=[], body=None):
    # name
    assert not name is None, "A function needs at least a name." # TODO: extend
    if isstring(name): name = Identifier(name)
    assert isinstance(name, Identifier), "A name should be an identifier"

    # type
    if type is None: type = VoidType()
    assert isinstance(type, Type), "Return-type should be a Type"

    # body
    if body is None: body = BlockStmt()

    # params
    if isinstance(params, list): params = ParameterList(params)
    assert isinstance(params, ParameterList)

    super(Function, self).__init__({"id":name, "type":type, 
                                    "params": params, "body": body})
    self.id     = name
    self.type   = type
    self.params = params
    self.body   = body

  def _children(self): return [self.body]
  children = property(_children)

class ParameterList(Fragment):
  def __init__(self, parameters):
    self.parameters = []
    [self.append(parameter) for parameter in parameters]
  def __iter__(self):
    return iter(self.parameters)
  def append(self, parameter):
    assert isinstance(parameter, Parameter)
    self.parameters.append(parameter)
    return self
  def __repr__(self): return "(" + ",".join(self.parameters) + ")"

class Parameter(Fragment):
  def __init__(self, name, type, default=None):
    # name
    if isstring(name): name = Identifier(name)
    assert isinstance(name, Identifier)
    # type
    assert isinstance(type, TypeExp)

    assert default == None or isinstance(default, Expression)
    self.name    = name
    self.type    = type
    self.default = default
  
# Statements

class Statement(Code): pass
class BlockStmt(Statement):
  def __repr__(self): return "== children"

class Print(WithoutChildren, Code):
  def __init__(self, string, *args):
    # string
    if isstring(string): string = StringLiteral(string)
    assert isinstance(string, StringLiteral)
    
    # TODO: assert args to be expressions

    super(Print, self).__init__({"string": string, "args": args})
    
    self.string = string
    self.args   = args

class Import(WithoutChildren, Code):
  def __init__(self, imported):
    # TODO: checking

    super(Import, self).__init__({"imported": imported})

    self.imported = imported

# Expressions

class Expression(Fragment): pass

# Literals

class StringLiteral(Fragment):
  def __init__(self, data):
    self.data = data
  def __repr__(self):
    return '"' + self.data.replace("\n", "\\n") + '"'

# Types

class Type(Fragment): pass
class VoidType(Type):
  def __repr__(self): return "void"

# A visitor for instructions = Code or Fragment

@visits([Fragment, Code])
class Visitor(): pass
