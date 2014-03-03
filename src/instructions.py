# instructions.py
# abstract instruction set, implemented as Code
# author: Christophe VG

from util.check   import isstring, isidentifier
from util.visitor import visits, novisiting
from util.types   import TypedList, Any

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
    if body is None: body = Block()

    # params
    if isinstance(params, list): params = ParameterList(params)
    assert isinstance(params, ParameterList)

    super(Function, self).__init__({"id":name, "type":type, "params": params})
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

class Statement(Code):
  def __init__(self, data):
    super(Statement, self).__init__(data)

class Block(Statement):
  def __init__(self):
    super(Statement, self).__init__({})

class IfStatement(WithoutChildModification, Statement):
  def __init__(self, expression, true_clause, false_clause=None):
    assert isinstance(expression, Expression)
    assert isinstance(true_clause, Statement)
    assert false_clause == None or isinstance(false_clause, Statement)
    self.expression   = expression
    self.true_clause  = true_clause
    self.false_clause = false_clause
  def _children(self): return [self.true_clause, self.false_clause]
  children = property(_children)

@novisiting
class MutUnOp(WithoutChildren, Statement):
  def __init__(self, operand):
    assert isinstance(operand, VariableExp)
    self.operand = operand
  def ends(self):
    return True

class Inc(MutUnOp): pass
class Dec(MutUnOp): pass

@novisiting
class ImmutUnOp(WithoutChildren, Statement):
  def __init__(self, operand):
    assert isinstance(operand, Expression)
    self.operand = operand
  def ends(self):
    return True

class Print(WithoutChildren, Statement):
  def __init__(self, string, *args):
    # string
    if isstring(string): string = StringLiteral(string)
    assert isinstance(string, StringLiteral)
    
    # TODO: assert args to be expressions

    super(Print, self).__init__({"string": string, "args": args})
    
    self.string = string
    self.args   = args

class Import(WithoutChildren, Statement):
  def __init__(self, imported):
    # TODO: checking
    super(Import, self).__init__({"imported": imported})
    self.imported = imported

class Raise(ImmutUnOp): pass

class Comment(ImmutUnOp):
  def __init__(self, comment):
    assert isstring(comment)
    self.comment = comment
  def __str__(self):
    return self.comment

@novisiting
class BinOp(Statement):
  def __init__(self, operand, expression):
    assert isinstance(operand, VariableExp)
    assert isinstance(expression, Expression)
    self.operand    = operand
    self.expression = expression
  def ends(self):
    return True

class Assign(BinOp): pass
class Add(BinOp): pass
class Sub(BinOp): pass

class Return(Statement):
  def __init__(self, expression=None):
    assert expression == None or isinstance(expression, Expression)
    self.expression = expression
  def ends(self):
    return True

@novisiting
class CondLoop(Statement):
  def __init__(self, condition, body):
    assert isinstance(condition, Expression)
    assert isinstance(body, Statement)
    self.condition = condition
    self.body      = body

class WhileDo(CondLoop): pass
class RepeatUntil(CondLoop): pass

class For(Statement):
  def __init__(self, init, check, change, body=None):
    assert isinstance(init,   Statement) and not isinstance(init,   Block)
    assert isinstance(check,  Expression)
    assert isinstance(change, Statement) and not isinstance(change, Block)
    if body == None:
      body = Block()
    else:
      assert isinstance(body, Block)
    self.init   = init
    self.check  = check
    self.change = change
    self.body   = body

class StructuredType(Statement):
  def __init__(self, name, properties=[]):
    if isstring(name): name = Identifier(name)
    assert isinstance(name, Identifier)
    super(StructuredType, self).__init__({"name":name})
    self.name       = name
    self.properties = TypedList(Any(Property, Comment), properties)
  def __repr__(self):
    return "struct " + self.name + \
           "(" + ",".join(",", [prop for prop in self.properties]) + ")"

class Property(Fragment):
  def __init__(self, name, type):
    assert isinstance(name, Identifier)
    assert isinstance(type, TypeExp), "expected TypeExp but got " + type.__class__.__name__
    self.name = name
    self.type = type
  def __repr__(self): return "property " + self.name + ":" + self.type

# Expressions

@novisiting
class Expression(Fragment): pass

@novisiting
class ExpressionList(Fragment):
  def __init__(self, expressions):
    self.expressions = []
    [self.append(expression) for expression in expressions]
  def __iter__(self):
    return iter(self.expressions)
  def append(self, expression):
    assert isinstance(expression, Expression)
    self.expressions.append(expression)
    return self

@novisiting
class Variable(Expression): pass

class SimpleVariable(Variable):
  def __init__(self, name):
    assert isinstance(name, Identifier)
    self.name = name

class Object(SimpleVariable): pass

class Property(Object):
  def __init__(self, obj, property):
    assert isinstance(obj, ObjectExp)
    assert isinstance(property, Identifier)
    self.obj  = obj
    self.prop = prop

@novisiting
class UnOp(Expression):
  def __init__(self, operand):
    assert isinstance(operand, Expression)
    self.operand = operand

class Not(UnOp): pass

@novisiting
class BinOp(Expression):
  def __init__(self, left, right):
    assert isinstance(left, Expression)
    assert isinstance(right, Expression)
    self.left  = left
    self.right = right

class And(BinOp): pass
class Or(BinOp): pass
class Equals(BinOp): pass
class NotEquals(BinOp): pass
class LT(BinOp): pass
class LTEQ(BinOp): pass
class GT(BinOp): pass
class GTEQ(BinOp): pass
class Plus(BinOp): pass
class Minus(BinOp): pass
class Mult(BinOp): pass
class Div(BinOp): pass
class Modulo(BinOp): pass

class FunctionCall(Expression):
  def __init__(self, function, arguments=[]):
    assert isinstance(function, Identifier)
    self.function  = function
    self.arguments = ExpressionList(arguments)
  def ends(self):
    return True

class MethodCall(Expression):
  def __init__(self, obj, method, arguments=[]):
    assert isinstance(obj, ObjectExp)
    assert isinstance(method, Identifier)
    self.obj       = obj
    self.method    = method
    self.arguments = ExpressionList(arguments)

# Literals

@novisiting
class Literal(Fragment): pass

class StringLiteral(Literal):
  def __init__(self, data):
    self.data = data
  def __repr__(self):
    return '"' + self.data.replace("\n", "\\n") + '"'

class BooleanLiteral(Literal):
  def __init__(self, value):
    assert isinstance(value, bool)
    self.value = value
  def __repr__(self):
    return "true" if self.value else "false"

class IntegerLiteral(Literal):
  def __init__(self, value):
    assert isinstance(value, int)
    self.value = value
  def __repr__(self):
    return str(self.value)
  
class FloatLiteral(Literal):
  def __init__(self, value):
    assert isinstance(value, float)
    self.value = value
  def __repr__(self):
    return str(self.value)

class ListLiteral(Literal):
  def __init__(self, expressions=[]):
    self.expressions = ExpressionList(expressions)
  def __repr__(self):
    return "[" + ",".join([expr for expr in self.expressions]) + "]"

class TupleLiteral(Literal):
  def __init__(self, expressions=[]):
    self.expressions = ExpressionList(expressions)
  def __repr__(self):
    return "(" + ",".join([expr for expr in self.expressions]) + ")"

class AtomLiteral(Literal):
  def __init__(self, name):
    assert isinstance(name, Identifier)
    self.name = name
  def __repr__(self):
    return "atom " + self.name

# Types

class Type(Fragment): pass
class VoidType(Type):
  def __repr__(self): return "void"

class ManyType(Type):
  def __init__(self, type):
    assert isinstance(type, Type)
    self.subtype = type
  def __repr__(self): return "many " + self.subtype

class ObjectType(Type):
  def __init__(self, class_name):
    assert isidentifier(clazz)
    self.class_name = class_name
  def __repr__(self): return "object " + self.class_name

class ByteType(Type):
  def __repr__(self): return "byte"

class IntegerType(Type):
  def __repr__(self): return "int"

class BooleanType(Type):
  def __repr__(self): return "bool"

class FloatType(Type):
  def __repr__(self): return "float"
  
class LongType(Type):
  def __repr__(self): return "long"

# A visitor for instructions = Code or Fragment

@visits([Fragment, Code])
class Visitor(): pass
