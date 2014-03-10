# instructions.py
# abstract instruction set, implemented as Code
# author: Christophe VG

from util.check   import isstring, isidentifier
from util.visitor import visits, novisiting
from util.types   import TypedList, Any

from codecanvas.base import Code, WithoutChildren, WithoutChildModification, List

# Mixins

class Identified(object):
  def get_name(self): return self.id.name
  name = property(get_name)

class Identifier(Code):
  def __init__(self, name):
    assert isidentifier(name), "Not an Identifier: " + name
    self.name = name
  def __repr__(self): return self.name

# Declarations

class Constant(Identified, Code):
  def __init__(self, id, value, type=None):
    # name
    if isstring(id): id = Identifier(id)
    assert isinstance(id, Identifier), "Name should be an identifier, not" + \
                                       id.__class__.__name__

    # TODO: add some value-checking ? (to avoid havoc)
    if isstring(value): value = Identifier(value)

    if type is None: type = VoidType()
    assert isinstance(type, Type), "Type should be a Type, not " + \
                                   type.__class__.__name__

    super(Constant, self).__init__({"id": id, "value": value, "type": type})
    self.id    = id
    self.value = value
    self.type  = type

class Function(Identified, Code):
  def __init__(self, name, type=None, params=[]):
    # name
    assert not name is None, "A function needs at least a name." # TODO: extend
    if isstring(name): name = Identifier(name)
    assert isinstance(name, Identifier), "Name should be an identifier, not" + \
                                         name.__class__.__name__

    # type
    if type is None: type = VoidType()
    assert isinstance(type, Type), "Return-type should be a Type, not " + \
                                   type.__class__.__name__

    # params
    if isinstance(params, list): params = TypedList(Parameter, params)

    super(Function, self).__init__({"id":name, "type":type, "params": params})
    self.id     = name
    self.type   = type
    self.params = params

class Parameter(Identified, Code):
  def __init__(self, id, type=None, default=None):
    # name
    if isstring(id): id = Identifier(id)
    assert isinstance(id, Identifier)
    # type
    if type is None: type = VoidType()
    assert isinstance(type, Type)

    assert default == None or isinstance(default, Expression)
    super(Parameter, self).__init__({"id": id, "type": type, "default": default})
    self.id      = id
    self.type    = type
    self.default = default
  
# Statements

class Statement(Code):
  def __init__(self, data):
    super(Statement, self).__init__(data)

class EmptyStatement(Statement):
  def __init__(self):
    super(EmptyStatement, self).__init__({})

class IfStatement(WithoutChildModification, Statement):
  def __init__(self, expression, true_clause, false_clause=[]):
    assert isinstance(expression, Expression)
    assert isinstance(true_clause, list)
    assert isinstance(false_clause, list)
    super(IfStatement, self).__init__({"expression": expression})
    self.expression   = expression
    self.true_clause  = true_clause
    self.false_clause = false_clause
  def _children(self): return [self.true_clause, self.false_clause]
  children = property(_children)

class CaseStatement(WithoutChildModification, Statement):
  def __init__(self, expression, cases, consequences):
    assert isinstance(expression, Expression)
    assert isinstance(cases, list)
    assert isinstance(consequences, list)
    super(CaseStatement, self).__init__({"expression": expression})
    self.expression   = expression
    self.cases        = cases
    self.consequences = consequences
  def _children(self): return [self.cases, self.consequences]
  children = property(_children)

@novisiting
class MutUnOp(WithoutChildren, Statement):
  def __init__(self, operand):
    assert isinstance(operand, Variable)
    super(MutUnOp, self).__init__({"op": operand})
    self.operand = operand
  def ends(self):
    return True

class Inc(MutUnOp): pass
class Dec(MutUnOp): pass

@novisiting
class ImmutUnOp(WithoutChildren, Statement): pass

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
    super(Comment, self).__init__({"comment": comment})
    self.comment = comment
  def __str__(self):
    return "# " + self.comment

@novisiting
class BinOp(Statement):
  def __init__(self, operand, expression):
    assert isinstance(operand, Variable)
    assert isinstance(expression, Expression)
    Statement.__init__(self, {"operand": operand, "expression": expression})
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
    super(Return, self).__init__({})
    self.expression = expression
  def ends(self):
    return True

@novisiting
class CondLoop(Statement):
  def __init__(self, condition):
    assert isinstance(condition, Expression)
    super(CondLoop, self).__init__({"condition": condition})
    self.condition = condition

class WhileDo(CondLoop): pass
class RepeatUntil(CondLoop): pass

class For(Statement):
  def __init__(self, init, check, change):
    assert isinstance(init,   Statement) and not isinstance(init,   Block)
    assert isinstance(check,  Expression)
    assert isinstance(change, Statement) and not isinstance(change, Block)
    super(For, self).__init__({"init": init, "check": check, "change": change})
    self.init   = init
    self.check  = check
    self.change = change

class StructuredType(Statement):
  def __init__(self, name, properties=[]):
    if isstring(name): name = Identifier(name)
    assert isinstance(name, Identifier)
    super(StructuredType, self).__init__({"name":name})
    self.name       = name
  def __repr__(self):
    return "struct " + self.name + \
           "(" + ",".join(",", [prop for prop in self]) + ")"

class Property(WithoutChildModification, Code):
  def __init__(self, name, type):
    if isstring(name): name = Identifier(name)
    assert isinstance(name, Identifier)
    assert isinstance(type, Type), "expected Type but got " + type.__class__.__name__
    super(Property, self).__init__({"name": name, "type": type})
    self.name = name
    self.type = type
  def __repr__(self): return "property " + self.name + ":" + self.type

# Expressions

@novisiting
class Expression(Code): pass

@novisiting
class Variable(Expression): pass

class SimpleVariable(Identified, Variable):
  def __init__(self, id):
    if isstring(id): id = Identifier(id)
    assert isinstance(id, Identifier)
    super(SimpleVariable, self).__init__({"id": id})
    self.id = id

class Object(Identified, Variable):
  def __init__(self, id):
    if isstring(id): id = Identifier(id)
    assert isinstance(id, Identifier)
    super(Object, self).__init__({"id": id})
    self.id = id

class ObjectProperty(Variable):
  def __init__(self, obj, prop):
    assert isinstance(obj, Object)
    assert isinstance(prop, Identifier)
    super(ObjectProperty, self).__init__({"obj" : obj, "prop": prop})
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
    super(BinOp, self).__init__({"left": left, "right": right})
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

class Call(Expression):
  def __init__(self, info, arguments=[]):
    info["arguments"] = len(arguments)
    super(Call, self).__init__(info)
    self.arguments = TypedList(Expression, arguments)
  def ends(self):
    return True

class FunctionCall(Call):
  def __init__(self, function, arguments=[]):
    if isstring(function): function = Identifier(function)
    assert isinstance(function, Identifier)
    super(FunctionCall, self).__init__({"function": function}, arguments)
    self.function  = function

class MethodCall(Call):
  def __init__(self, obj, method, arguments=[]):
    assert isinstance(obj, Object) or isinstance(obj, ObjectProperty), \
           "Expected Object(Property), but got " + obj.__class__.__name__
    if isstring(method): method = Identifier(method)
    assert isinstance(method, Identifier)
    super(MethodCall, self).__init__({"obj": obj, "method": method}, arguments)
    self.obj       = obj
    self.method    = method

# Literals

@novisiting
class Literal(Expression): pass

class StringLiteral(Literal):
  def __init__(self, data):
    self.data = data
  def __repr__(self):
    return '"' + self.data.replace("\n", "\\n") + '"'

class BooleanLiteral(Literal):
  def __init__(self, value):
    assert isinstance(value, bool)
    super(BooleanLiteral, self).__init__({"value": value})
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
  def __init__(self):
    super(ListLiteral, self).__init__({})
  def __repr__(self):
    return "[]"

class TupleLiteral(Literal):
  def __init__(self, expressions=[]):
    self.expressions = TypedList(Expression, expressions)
  def __repr__(self):
    return "(" + ",".join([expr for expr in self.expressions]) + ")"

class AtomLiteral(Identified, Literal):
  def __init__(self, id):
    if isstring(id): id = Identifier(id)
    assert isinstance(id, Identifier)
    super(AtomLiteral, self).__init__({"name": id.name})
    self.id = id
  def __repr__(self):
    return "atom " + self.name

# Types

class Type(Code): pass

class NamedType(Type):
  def __init__(self, name):
    assert isstring(name)
    self.name = name
  def __repr__(self): return "type " + self.name
  
class VoidType(Type):
  def __repr__(self): return "void"

class ManyType(Type):
  def __init__(self, type):
    assert isinstance(type, Type), \
           "Expected Type but got " + type.__class__.__name__
    super(ManyType, self).__init__({})
    self.type = type
  def __repr__(self): return "many " + str(self.type)

class TupleType(Type):
  def __init__(self, types):
    for type in types:
      assert isinstance(type, Type)
    self.types = types
  def __repr__(self): return "tuple " + ",".join(self.types)

class ObjectType(Type):
  def __init__(self, name):
    assert isidentifier(name), name + " is no identifier"
    self.name = name
  def __repr__(self): return "object " + self.name

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

# Matching

class Match(Expression):
  def __init__(self, comp, expression=None):
    assert isinstance(comp, Comparator), \
           "Expected Comparator but got " + comp.__class__.__module__ + ":" + comp.__class__.__name__
    assert expression == None or isinstance(expression, Expression)
    super(Match, self).__init__({"comp": comp})
    self.comp       = comp
    self.expression = expression

class Comparator(Code):
  def __init__(self, operator):
    assert operator in [ "<", "<=", ">", ">=", "==", "!=", "!", "*" ]
    super(Comparator, self).__init__({"operator": operator})
    self.operator = operator

class Anything(Comparator):
  def __init__(self):
    super(Anything, self).__init__("*")

# A visitor for instructions = Code or Code

@visits([Code])
class Visitor(): pass
