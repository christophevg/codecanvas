# instructions.py
# abstract instruction set, implemented as Code
# author: Christophe VG

from util.check import isstring, isidentifier

from codecanvas import Code, WithoutChildren, WithoutChildModification, List

# Mixins

class Identified(object):
  def get_name(self): return self.id.name
  name = property(get_name)

# Fragments - are instructions that aren't Codes by itself

class Fragment(object):
  def __init__(self, *args): pass

class Identifier(Fragment):
  def __init__(self, name):
    assert isidentifier(name), "Not an Identifier: " + name
    self.name = name

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
    if isinstance(params, list): params = ParamList(params)
    assert isinstance(params, ParamList)

    super(Function, self).__init__({"id":name, "type":type, 
                                    "params": params, "body": body})
    self.id     = name
    self.type   = type
    self.params = params
    self.body   = body

  def _children(self): return [self.params, self.body]
  children = property(_children)

class ParamList(List): pass

class Print(WithoutChildren, Code):
  def __init__(self, string, *args):
    # string
    if isstring(string): string = StringLiteral(string)
    assert isinstance(string, StringLiteral)
    
    # TODO: assert args to be expressions
    self.string =string
    self.args = args

# Statements

class Statement(Code): pass
class BlockStmt(Statement): pass

# Expressions

class Expression(Fragment): pass

# Literals

class StringLiteral(Fragment): pass

# Types

class Type(Fragment): pass
class VoidType(Type): pass
