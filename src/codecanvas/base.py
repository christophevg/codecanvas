# codecanvas.py
# creates hierarchically accessible code-structures
# author: Christophe VG

# helper functions to wrap return values in a list or not

def maybe_list(codes):
  if   len(codes) < 1:  return None
  elif len(codes) == 1: return codes[0]
  else:                 return List(codes)

def as_list(codes):
  if   codes is None:            return []
  elif isinstance(codes, list):  return codes
  elif isinstance(codes, List):  return list(codes)
  elif isinstance(codes, tuple): return codes[0].codes
  else:                          return [codes]

# the single code/node class

class Code(object):
  def __init__(self, data=""):
    self.data     = data
    self.stick_to = None
    self.tags     = []
    self.sticking = {"top":[], "bottom": []}
    self.floating = []
    self.bottom   = []
    self._parent  = None

  def _children(self):
    return self.sticking["top"] + self.floating + self.sticking["bottom"]
  children = property(_children)

  def _sticky(self):
    return not self.stick_to is None
  sticky = property(_sticky)

  def __str__(self):
    children = ""
    if len(self) > 0:
      for child in self.children:
        children += "\n" + \
                    "\n".join(["  " + line for line in str(child).split("\n")])
    tags     = "" if len(self.tags) < 1 else " [" + ",".join(self.tags) + "]"
    sticky   = "" if not self.sticky else " <sticky>"
    me       = "" if self.__class__.__name__ == "Code" \
                  else self.__class__.__name__ + " "
    return me + str(self.data) + tags + sticky + children

  def __iter__(self):
    return iter(self.children)

  def __len__(self):
    return len(self.children)

  def __getitem__(self, index):
    return self.children[index]

  def stick_top(self):
    if self.stick_to == "top": return
    if self._parent:
      if self.sticky: self._parent.sticking["bottom"].remove(self)
      else:           self._parent.floating.remove(self)
      self._parent.sticking["top"].append(self)
    self.stick_to = "top"
    return self

  def stick_bottom(self):
    if self.stick_to == "bottom": return
    if self._parent:
      if self.sticky: self._parent.sticking["top"].remove(self)
      else:           self._parent.floating.remove(self)
      self._parent.sticking["bottom"].append(self)
    self.stick_to = "bottom"
    return self

  def unstick(self):
    if not self.sticky: return
    if self._parent:
      self._parent.sticking[self.stick_to].remove(self)
      self._parent.floating.append(self)
    self.stick_to = None
    return self

  def tag(self, *tags):
    self.tags.extend(tags)
    self.tags = sorted(list(set(self.tags)))
    return self

  def untag(self, *tags):
    self.tags = filter(lambda x: not x in tags, self.tags)
    return self

  def append(self, *children):
    for child in children:
      child._parent = self
      if child.sticky: self.sticking[child.stick_to].append(child)
      else: self.floating.append(child)
    return maybe_list(children)

  def contains(self, *children):
    self.append(*children)
    return self

  def _insert(self, relative, *siblings):
    if self._parent is None: raise RuntimeError, self + " has no parent"
    if self.sticky: raise RuntimeError, self + " is sticky, can't insert"
    index = self._parent.floating.index(self) + relative
    for sibling in siblings:
      if sibling.sticky: raise RuntimeError, sibling + " is sticky, can't insert"
      sibling._parent = self._parent
      self._parent.floating.insert(index, sibling)
    return maybe_list(siblings)

  def insert_before(self, *siblings):
    for sibling in siblings:
      sibling._insert(0, self)
    return self

  def insert_after(self, *siblings):
    for sibling in siblings:
      sibling._insert(1, self)
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
      if tag in child.tags or tag == "*":
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
      def visit_all(self, code):
        if tags.issubset(code.tags): codes.append(code)
        for child in code.children: child.accept(self)
    self.accept(Finder())
    return maybe_list(codes)

  def accept(self, visitor):
    # try _all
    try: getattr(visitor, "visit_all")(self)
    except AttributeError: pass

    # try _specific_class_implementation
    try: return getattr(visitor, "visit_" + self.__class__.__name__)(self)
    except AttributeError: pass
    return ""

# wrapper for multiple Codes, offering the same interface, dispatching to list
# of Codes and aggregating results

class List(Code):
  def __init__(self, codes=[]):
    self.codes = codes

  def _children(self): return self.codes
  children = property(_children)

  def __iter__(self):
    return iter(self.codes)

  def __len__(self):
    return len(self.codes)

  def __getitem__(self, index):
    return self.codes[index]

  def stick_top(self):
    for code in self.codes: code.stick_top()
    return self

  def stick_bottom(self):
    for code in self.codes: code.stick_bottom()
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

  def insert_before(self, *siblings):
    siblings = as_list(siblings)
    for code in self.codes: code.insert_before(*siblings)
    return self

  def insert_after(self, *siblings):
    siblings = as_list(siblings)
    for code in self.codes: code.insert_after(*siblings)
    return self

  def insert_after(self, *siblings):
    for code in self.codes: code.insert_after(*siblings)
    return self

  def contains(self, *children):
    for code in self.codes: code.contains(*children)
    return self

  def select(self, *tags):
    selected = []
    for code in self.codes: selected.extend(as_list(code.select(*tags)))
    return maybe_list(selected)

  def find(self, *tags):
    selected = []
    for code in self.codes: selected.extend(as_list(code.find(*tags)))
    return maybe_list(selected)

class Canvas(Code):
  def __str__(self):
    return "\n".join([str(child) for child in self.children])

class Visitor(object):
  """
  Base-class for CodeCanvas-Visitors
  """
  def visit_all(self, code): pass
  def visit_Code(self, code): pass
  def visit_List(self, list):  pass

# Code implementations to override default functionality

class WithoutChildModification(object):
  def append(self, *children):        raise NotImplementedError
  def contains(self, *children):      raise NotImplementedError
  def insert_before(self, *siblings): raise NotImplementedError
  def insert_after(self, *siblings):  raise NotImplementedError

class WithoutChildren(WithoutChildModification):
  def _children(self): raise NotImplementedError
  children = property(_children)
  def __len__(self): return 0
