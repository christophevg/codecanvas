# examples.py
# tests CodeCanvas functionality
# author: Christophe VG

import unittest

from src.codecanvas import Code, List, Canvas

class TestExamples(unittest.TestCase):
  
  def test_readme(self):
    # create a canvas
    canvas = Canvas()

    # add code and tag them for later access
    canvas.append(Code("1")).tag("code1")
    canvas.append(Code("2")).tag("code2")

    # add hierarchical code, access through variables
    code1b = canvas.select("code1").append(Code("1b")).tag("code1b")
    Code("1a").tag("code1a").insert_before(code1b)
  
    # add more tags and access multiple tags globally
    canvas.select("code1", "code1a").tag("child")
    canvas.select("code1", "code1b").tag("child")
    canvas.select("code1").append(Code("1c")).tag("child")
    canvas.select("code1").append(Code("1d")).tag("child")
    canvas.find("child").tag("child of code1")
  
    # append accepts multiple arguments and result allows all to be tagged
    canvas.select("code2").append(Code("2a").tag("code2a"),
                                  Code("2b").tag("code2b"),
                                  Code("2c").tag("code2c")
                                 ).tag("child")
  
    # localized actions
    canvas.select("code2", "child").tag("child of code2")
  
    # mark code sticky and force order of children
    canvas.select("code1", "code1a").stick_top()
    Code("1aa").insert_before(canvas.select("code1", "code1b"))
    Code("2aa").insert_before(canvas.select("code2", "code2b"))
  
    self.assertEqual("\n" + str(canvas), """
1 [code1]
  1a [child,child of code1,code1a] <sticky>
  1aa
  1b [child,child of code1,code1b]
  1c [child,child of code1]
  1d [child,child of code1]
2 [code2]
  2a [child,child of code2,code2a]
  2aa
  2b [child,child of code2,code2b]
  2c [child,child of code2,code2c]""")

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestExamples)
  unittest.TextTestRunner(verbosity=2).run(suite)
