# visitor.py
# an abstract Visitor and Visitable base-class, providing the redirection
# author: Christophe VG

import inspect
import sys

class Visitable(object):
  """
  Baseclass for visitable classes
  """
  def visited(self):
    return self.__class__.__name__

  def accept(self, visitor):
    class_name  = self.visited()
    method_name = "visit_" + class_name
    return getattr(visitor, method_name)(self)

class Visitor(object):
  """
  Baseclass for visitors.
  """
  def check_coverage(self):
    """
    Function to see which handling functions are still missing.
    """
    methods = inspect.getmembers(self, predicate=inspect.ismethod)
    for name, method in methods:
      if name[:5] == "visit_":
        try: method(None)
        except AttributeError: pass

novisitings = []
def novisiting(clazz):
  novisitings.append(clazz.__module__ + "." + clazz.__name__)
  return clazz

class visits(object):
  """
  Decorator @visitors([superclass]) makes a decorated class a visitor for all
  classes in the module of the decorated class. The visitable classes can be
  limited to a number of common superclasses.
  """
  def __init__(self, supers=[]):
    self.supers = supers

  def __call__(self, visitor):
    # make the visitor a subclass of Visitor
    visitor = type(visitor.__name__, (Visitor,), dict(visitor.__dict__))

    # retrieve calling module and its classes
    frame   = inspect.stack()[1]
    module  = inspect.getmodule(frame[0])
    classes = inspect.getmembers(module, inspect.isclass)

    # dynamically adding all Stmt subclasses to the visitor
    def NotImplemented(name):
      def dummy(self, *args):
        print self.__class__.__name__, ": missing implementation for", name
      return dummy

    for name, clazz in classes:
      method_name = "visit_" + name
      if not method_name in dir(visitor):
        fqn = module.__name__ + "." + name
        if fqn not in novisitings:
          if super == [] or any([issubclass(clazz, sup) for sup in self.supers]):
            setattr(visitor, "visit_" + name, NotImplemented("visit_" + name))

    return visitor

def stacked(method):
  """
  Decorator for methods to keep track of their execution using a stack.
  """
  def wrapped(self, obj):
    self._stack.append(obj)
    method(self, obj)
    self._stack.pop()
  return wrapped

def with_handling(method):
  """
  Decorator for methods of the Visitor to perform actual handling before or
  after the Visitor visits its children.
  """
  def execute(self, name, obj):
    # TODO: find nicer Pythonic way to structure this :-(
    try:
      # get and execute actual handling
      getattr(self, name)(obj)
    except AttributeError, e:
      expected = "'{0}' object has no attribute '{1}'".format(
                   self.__class__.__name__, name)
      if str(e) != expected:
        # Whoops some other AttributeError ... while calling
        raise
      else:
        # no handler, that's ok
        pass

  obj_name = method.__name__[len("visit_"):]  # extract object name from method 

  def wrapped(self, obj):
    execute(self, "before_visit_" + obj_name, obj)
    method(self, obj)
    execute(self, "after_visit_" + obj_name, obj)

  return wrapped
