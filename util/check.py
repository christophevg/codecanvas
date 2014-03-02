# check.py
# some additional check functions
# author: Christophe VG

import re
identifier = re.compile(r"^[^\d\W]\w*\Z")

def isstring(candidate):
  """
  Asserts that a given candidate is a string, both "normal" or unicode.
  """
  return isinstance(candidate, str) or isinstance(candidate, unicode)

def isidentifier(candidate):
  """
  Asserts that a given candidate is a string with identifier limitations
  """
  return isstring(candidate) and (re.match(identifier, candidate) is not None)
