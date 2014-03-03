# types.py
# types with extended functionality, mostly typed lists,...
# author: Christophe VG

from collections import OrderedDict

class NamedTypedOrderedDict(object):
  def __init__(self, type):
    self.objects = OrderedDict()
    self.type    = type

  def items(self):
    return self.objects.items()

  def __iter__(self):
    return iter(self.objects.values())

  def __contains__(self, key):
    return key in self.objects

  def __getitem__(self, key):
    return self.objects[key]

  def __setitem__(self, key, value):
    self.objects[key] = value

  def append(self, obj):
    assert isinstance(obj, self.type)
    self.objects[obj.name] = obj
    return self

  def __str__(self):
    return "NamedTypedOrderedDict(" + self.type.__name__ + ")"

class TypedList(object):
  def __init__(self, type, objects=[]):
    self.objects = []
    self.type    = type
    [self.append(obj) for obj in objects]

  def __iter__(self):
    return iter(self.objects)

  def __getitem__(self, index):
    try: return self.objects[index]
    except: return None

  def __len__(self):
    return len(self.objects)

  def index(self, obj):
    try: return self.objects.index(obj)
    except: return None

  def append(self, obj):
    if isinstance(self.type, Any):
      assert self.type.isa(obj), \
             "TypedList's provided obj is a " + + obj.__class__.__name__ + \
             " but expected " + str(self.type.__name__)
    else:
      assert isinstance(obj, self.type), \
             "TypedList's provided obj is a " + + obj.__class__.__name__ + \
             " but expected " + self.type.__name__
    self.objects.append(obj)
    return self

  def __str__(self):
    return "TypedList(" + self.type.__name__ + ")"

class Any(object):
  def __init__(self, *args):
    self.types = args

  def isa(self, type):
    for possibility in self.types:
      if isinstance(type, possibility): return True
    return False

  def __str__(self):
    return "Any(" + ",".join([t.__class__.__name__ for t in self.types]) + ")"
