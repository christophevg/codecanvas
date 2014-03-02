# structure.py
# Structure builders for CodeCanvas
# author: Christophe VG

import codecanvas

class Unit(codecanvas.Canvas):
  """
  Unit is a simple alias for Canvas
  """
  pass

class AutoTag(codecanvas.Code):
  """
  AutoTag extends a simple Code with autotagging based on its data, which is
  considered a name.
  """
  def __init__(self, name):
    assert name != None, "A name is required, and can't be None."
    super(AutoTag, self).__init__(name)
    self.tag(name)
  def get_name(self): return self.data
  name = property(get_name)

class Module(AutoTag):
  """
  Module represents a functional module and by default provides two sections:
  one for definitions (read: headers) and one for declarations (read: your code)
  """
  def __init__(self, name):
    super(Module, self).__init__(name)
    self.append(Section("def"), Section("dec"))

class Section(AutoTag):
  """
  Section is a simple structure builder and alias for an auto-tagging Code.
  """
  pass
