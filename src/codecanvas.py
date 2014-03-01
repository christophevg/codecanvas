# codecanvas.py
# creates hierarchically accessible code-structures
# author: Christophe VG <contact@christophe.vg>

# helper functions to wrap return values in a list or not

def maybe_list(codes):
  if   len(codes) < 1:  return None
  elif len(codes) == 1: return codes[0]
  else:                 return List(codes)

def as_list(codes):
  if   codes is None:           return []
  elif isinstance(codes, list): return codes
  elif isinstance(codes, List): return list(codes)
  else:                         return [codes]

# the single code/node class

class Code(object):
  def __init__(self, data):
    self.data     = data
    self.sticky   = False
    self.tags     = []
    self.children = []
    self._parent  = None

  def __str__(self):
    children = ""
    if len(self.children) > 0:
      for child in self.children:
        children += "\n" + \
                    "\n".join(["  " + line for line in str(child).split("\n")])
    tags     = "" if len(self.tags) < 1 else " [" + ",".join(self.tags) + "]"
    sticky   = "" if not self.sticky else " <sticky>"
    return str(self.data) + tags + sticky + children

  def stick(self):
    self.sticky = True
    return self

  def unstick(self):
    self.sticky = False
    return self

  def tag(self, *tags):
    self.tags.extend(tags)
    self.tags = list(set(self.tags))
    return self

  def untag(self, *tags):
    self.tags = filter(lambda x: not x in tags, self.tags)
    return self

  def append(self, *children):
    for child in children:
      child._parent = self 
    self.children.extend(children)
    return maybe_list(children)

  def contain(self, *children):
    self.append(*children)
    return self

  def select(self, *tags):
    """
    Selects children of which the chain up to them is marked with tags.
    """
    if len(tags) < 1: return None
    codes = []
    tag   = tags[0]
    more  = len(tags) > 1
    for child in self.children:
      if tag in child.tags:
        if more: codes.extend(as_list(child.select(*tags[1:])))
        else:    codes.append(child)
    return maybe_list(codes)

  def find(self, *tags):
    """
    Finds codes that have tags.
    """
    tags = set(tags)
    codes = []
    class Finder(Visitor):
      def before_visit(self, code):
        if tags.issubset(code.tags): codes.append(code)
    self.accept(Finder())
    return maybe_list(codes)

  def accept(self, visitor):
    # allow the visitor to specify actions before
    try: getattr(visitor, "before_visit")(self)
    except AttributeError: pass
    
    # recurse down the children
    for child in self.children: child.accept(visitor)

    # allow the visitor to specify actions before
    try: getattr(visitor, "after_visit")(self)
    except AttributeError: pass

# wrapper for multiple Codes, offering the same interface, dispatching to list
# of Codes and aggregating results

class List(object):
  def __init__(self, codes=[]):
    self.codes = codes

  def __iter__(self):
    return iter(self.codes)

  def stick(self):
    for code in self.codes: code.stick()
    return self

  def unstick(self):
    for code in self.codes: code.unstick()
    return self

  def tag(self, *tags):
    for code in self.codes: code.tag(*tags)
    return self

  def untag(self, *tags):
    for code in self.codes: code.untag(*tags)
    return self

  def append(self, *children):
    for code in self.codes: code.append(*children)
    return maybe_list(children)

  def contain(self, *children):
    for code in self.codes: code.contain(*children)
    return self

  def select(self, *tags):
    selected = []
    for code in self.codes: selected.extend(as_list(code.select(*tags)))
    return maybe_list(selected)

  def find(self, *tags):
    selected = []
    for code in self.codes: selected.extend(as_list(code.find(*tags)))
    return maybe_list(selected)

  def accept(self, visitor):
    # allow the visitor to specify actions before
    try: getattr(visitor, "before_visit_list")(self)
    except AttributeError: pass
    
    # recurse down the wrapped codes
    for code in self.codes: code.accept(visitor)

    # allow the visitor to specify actions before
    try: getattr(visitor, "after_visit_list")(self)
    except AttributeError: pass

class Canvas(Code): pass

class Visitor(object):
  """
  Base-class for CodeCanvas-Visitors
  """
  def before_visit(self, code): pass
  def after_visit(self, code):  pass

  def before_visit_list(self, code): pass
  def after_visit_list(self, code):  pass
