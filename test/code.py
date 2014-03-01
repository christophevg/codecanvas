# codecanvas.py
# tests CodeCanvas functionality
# author: Christophe VG

import unittest

from src.codecanvas import Code, List

class TestCodeCanvas(unittest.TestCase):
  
  def test_code_data(self):
    code = Code("something")
    self.assertEqual(str(code), "something")

  def test_code_stick(self):
    code = Code("something").stick()
    self.assertEqual(str(code), "something <sticky>")

  def test_code_unstick(self):
    code = Code("something").stick().unstick()
    self.assertEqual(str(code), "something")

  def test_code_tag(self):
    code = Code("something").tag("tagged")
    self.assertEqual(str(code), "something [tagged]")

  def test_code_multiple_tags(self):
    code = Code("something").tag("tagged", "more")
    self.assertEqual(str(code), "something [tagged,more]")

  def test_code_duplicate_tags(self):
    code = Code("something").tag("tagged", "more").tag("more")
    self.assertEqual(str(code), "something [tagged,more]")

  def test_code_untag(self):
    code = Code("something").tag("tagged", "more", "even more").untag("more")
    self.assertEqual(str(code), "something [tagged,even more]")

  def test_append_child(self):
    code = Code("something")
    code.append(Code("child1"))
    self.assertEqual(str(code), "something\n  child1")

  def test_append_multiple_children(self):
    code = Code("something")
    code.append(Code("child1"), Code("child2"), Code("child3"))
    self.assertEqual(str(code), "something\n  child1\n  child2\n  child3")

  def test_containing_structure(self):
    code = Code("something").contain(
             Code("child1").tag("child", "1").stick(),
             Code("child2").tag("child", "2").contain(
               Code("child2a").tag("grandchild", "a"),
               Code("child2b").tag("grandchild", "b").contain(
                 Code("child2b1").tag("grandgrandchild"),
                 Code("child2b2").tag("grandgrandchild")
               ),
               Code("child2c").tag("grandchild", "c")
             ),
             Code("child3").tag("child", "3").stick()
           )
    # mind that due to internal use of set, the order of tags is affected !
    self.assertEqual(str(code), """something
  child1 [1,child] <sticky>
  child2 [2,child]
    child2a [a,grandchild]
    child2b [b,grandchild]
      child2b1 [grandgrandchild]
      child2b2 [grandgrandchild]
    child2c [c,grandchild]
  child3 [3,child] <sticky>""")

  def test_select_single_child(self):
    code = Code("something")
    child1 = code.append(Code("child1")).tag("one")
    child2 = code.append(Code("child2")).tag("two")
    child3 = code.append(Code("child3")).tag("three")
    self.assertIs(code.select("two"), child2)
    self.assertIsNone(code.select("mr pink"))
  
  def test_select_single_grandchild(self):
    code = Code("something")
    child1 = code.append(Code("child1")).tag("one")
    child2 = code.append(Code("child2")).tag("two")
    child3 = code.append(Code("child3")).tag("three")
    grandchild1 = child1.append(Code("grandchild1")).tag("grandchild")
    grandchild2 = child2.append(Code("grandchild2")).tag("grandchild")
    grandchild3 = child3.append(Code("grandchild3")).tag("grandchild")
    self.assertIs(code.select("two", "grandchild"), grandchild2)
    self.assertIsNone(code.select("two", "mr pink"))

  def test_find_single_grandchild(self):
    code = Code("something").contain(
             Code("child1").tag("child", "1").stick(),
             Code("child2").tag("child", "2").contain(
               Code("child2a").tag("grandchild", "a"),
               Code("child2b").tag("grandchild", "b").contain(
                 Code("child2b1").tag("grandgrandchild"),
                 Code("child2b2").tag("mr pink")
               ),
               Code("child2c").tag("grandchild", "c")
             ),
             Code("child3").tag("child", "3").stick()
           )
    # mind that due to internal use of set, the order of tags is affected !
    self.assertEqual(code.find("mr pink").data, "child2b2")
    self.assertIsNone(code.find("mr red"))

  def test_find_with_multiple_tags(self):
    code = Code("something").contain(
             Code("child1").tag("child", "1").stick(),
             Code("child2").tag("child", "2").contain(
               Code("child2a").tag("grandchild", "a"),
               Code("child2b").tag("grandchild", "b").contain(
                 Code("child2b1").tag("grandgrandchild"),
                 Code("child2b2").tag("grand", "child", "2")
               ),
               Code("child2c").tag("grandchild", "c")
             ),
             Code("child3").tag("child", "3").stick()
           )
    l = code.find("child", "2")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l.codes), 2)
    self.assertEqual(l.codes[0].data, "child2")
    self.assertEqual(l.codes[1].data, "child2b2")

  # CodeLists can be returned by append, select or find
  def test_append_multiple_children_returns_codelist(self):
    l = Code("something").append(Code("child1"), Code("child2"), Code("child3"))
    self.assertIsInstance(l, List)
    self.assertEqual(len(l.codes), 3)
    self.assertEqual(l.codes[0].data, "child1")
    self.assertEqual(l.codes[1].data, "child2")
    self.assertEqual(l.codes[2].data, "child3")

  def test_select_multiple_children_returns_codelist(self):
    code = Code("something").contain(
             Code("child1").tag("child", "1").stick(),
             Code("child2").tag("BASTARD", "2").contain(
               Code("child2a").tag("grandchild", "a"),
               Code("child2b").tag("grandchild", "b").contain(
                 Code("child2b1").tag("grandgrandchild"),
                 Code("child2b2").tag("mr pink")
               ),
               Code("child2c").tag("grandchild", "c")
             ),
             Code("child3").tag("child", "3").stick()
           )
    l = code.select("child")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l.codes), 2)
    self.assertEqual(l.codes[0].data, "child1")
    self.assertEqual(l.codes[1].data, "child3")

  def test_find_multiple_children_returns_codelist(self):
    code = Code("something").contain(
             Code("child1").tag("child", "1").stick(),
             Code("child2").tag("child", "2").contain(
               Code("child2a").tag("grandchild", "a"),
               Code("child2b").tag("grandchild", "b").contain(
                 Code("child2b1").tag("grandgrandchild", "a"),
                 Code("child2b2").tag("mr pink", "b")
               ),
               Code("child2c").tag("grandchild", "c")
             ),
             Code("child3").tag("child", "3").stick()
           )
    l = code.find("b")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l.codes), 2)
    self.assertEqual(l.codes[0].data, "child2b")
    self.assertEqual(l.codes[1].data, "child2b2")

  # TODO

  def test_stick_codelist(self): pass
  def test_untstick_codelist(self): pass

  def test_tag_codelist(self): pass
  def test_untag_codelist(self): pass
  
  def test_append_codelist(self): pass
  def test_contain_codelist(self): pass
  def test_select_codelist(self): pass
  def test_find_codelist(self): pass

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestCodeCanvas)
  unittest.TextTestRunner(verbosity=2).run(suite)
