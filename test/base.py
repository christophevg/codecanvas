# codecanvas.py
# tests CodeCanvas functionality
# author: Christophe VG

import unittest

from codecanvas.base import Code, List

class TestBase(unittest.TestCase):
  
  def test_code_data(self):
    code = Code("something")
    self.assertEqual(str(code), "something")

  def test_code_stickyness(self):
    code = Code("something").stick_top()
    self.assertEqual(str(code), "something <sticky>")
    code = Code("something").stick_bottom()
    self.assertEqual(str(code), "something <sticky>")

  def test_code_unstick(self):
    code = Code("something").stick_top().unstick()
    self.assertEqual(str(code), "something")

  def test_code_tag(self):
    code = Code("something").tag("tagged")
    self.assertEqual(str(code), "something [tagged]")

  def test_code_multiple_tags(self):
    code = Code("something").tag("tagged", "more")
    self.assertEqual(str(code), "something [more,tagged]")

  def test_code_duplicate_tags(self):
    code = Code("something").tag("tagged", "more").tag("more")
    self.assertEqual(str(code), "something [more,tagged]")

  def test_code_untag(self):
    code = Code("something").tag("tagged", "more", "even more").untag("more")
    self.assertEqual(str(code), "something [even more,tagged]")

  def test_append_child(self):
    code = Code("something")
    code.append(Code("child1"))
    self.assertEqual(str(code), "something\n  child1")

  def test_append_multiple_children(self):
    code = Code("something")
    code.append(Code("child1"), Code("child2"), Code("child3"))
    self.assertEqual(str(code), "something\n  child1\n  child2\n  child3")

  def test_insert(self):
    code = Code("something")
    child2 = code.append(Code("child2"))
    child1 = Code("child1").insert_before(child2)
    Code("child3").insert_after(child1)
    self.assertEqual(str(code), "something\n  child1\n  child3\n  child2")

  def create_code(self):
    return Code("something").contains(
             Code("child1").tag("child", "1", "sticky").stick_top(),
             Code("child2").tag("child", "2").contains(
               Code("child2a").tag("mr red", "grandchild", "a"),
               Code("child2b").tag("mr pink", "grandchild", "b").contains(
                 Code("child2b1").tag("great", "grand", "child", "b", "1"),
                 Code("child2b2").tag("great", "grand", "child", "b", "2")
               ),
               Code("child2c").tag("c")
             ),
             # note: child3 and child4 are swapped because child3 is sticked
             #       to the bottom !!!
             Code("child3").tag("child", "3", "sticky").stick_bottom(),
             Code("child4").tag("c")
           )

  def test_containing_structure(self):
    code = self.create_code()
    self.assertEqual(str(code), """something
  child1 [1,child,sticky] <sticky>
  child2 [2,child]
    child2a [a,grandchild,mr red]
    child2b [b,grandchild,mr pink]
      child2b1 [1,b,child,grand,great]
      child2b2 [2,b,child,grand,great]
    child2c [c]
  child4 [c]
  child3 [3,child,sticky] <sticky>""")

  def test_select_single_child(self):
    code = self.create_code()
    self.assertEqual(code.select("2").data, "child2")
    self.assertIsNone(code.select("mr pink"))
  
  def test_select_single_grandchild(self):
    code = self.create_code()
    self.assertEqual(code.select("2", "b").data, "child2b")
    self.assertIsNone(code.select("two", "mr pink"))

  def test_select_with_wildcard(self):
    code = Code("something").contains(
             Code("child1").tag("child", "1").contains(
               Code("child1a").tag("grand", "child", "a").contains(
                 Code("child1a1").tag("great-grand", "child", "1"),
                 Code("child1a2").tag("great-grand", "child", "2"),
                 Code("child1a3").tag("great-grand", "child", "3")
               ),
               Code("child1b").tag("grand", "child", "b").contains(
                 Code("child1b1").tag("great-grand", "child", "1"),
                 Code("child1b2").tag("great-grand", "child", "2", "bastard"),
                 Code("child1b3").tag("great-grand", "child", "3")
               ),
               Code("child1c").tag("grand", "child", "c").contains(
                 Code("child1c1").tag("great-grand", "child", "1"),
                 Code("child1c2").tag("great-grand", "child", "2"),
                 Code("child1c3").tag("great-grand", "child", "3", "bastard")
               )
             ),
             Code("child2").tag("child", "2").contains(
               Code("child2a").tag("grand", "child", "a"),
               Code("child2b").tag("grand", "child", "b").contains(
                 Code("child2b1").tag("great-grand", "child", "1"),
                 Code("child2b2").tag("great-grand", "child", "2")
               ),
               Code("child2c").tag("grand", "child", "c")
             ),
             Code("child3").tag("no-child", "3").contains(
               Code("child3a").tag("unimportant").contains(
                 Code("child3a1").tag("bastard")
               )
             )
           )
    l = code.select("child", "*", "bastard")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l.codes), 2)
    self.assertEqual(l.codes[0].data, "child1b2")
    self.assertEqual(l.codes[1].data, "child1c3")

  def test_find_single_grandchild(self):
    code = self.create_code()
    # mind that due to internal use of set, the order of tags is affected !
    self.assertEqual(code.find("mr pink").data, "child2b")
    self.assertIsNone(code.find("mr yellow"))

  def test_find_with_multiple_tags(self):
    code = self.create_code()
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
    code = self.create_code()
    l = code.select("child")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l.codes), 3)
    self.assertEqual(l.codes[0].data, "child1")
    self.assertEqual(l.codes[1].data, "child2")
    self.assertEqual(l.codes[2].data, "child3")

  def test_find_multiple_children_returns_codelist(self):
    code = self.create_code()
    l = code.find("b")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l.codes), 3)
    self.assertEqual(l.codes[0].data, "child2b")
    self.assertEqual(l.codes[1].data, "child2b1")
    self.assertEqual(l.codes[2].data, "child2b2")

  # list iterator and indexing

  def test_codelist_len_and_iterator(self):
    code = self.create_code()
    l = code.select("child")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l.codes), 3)
    self.assertEqual(len(l), 3)
    self.assertEqual([c.data for c in l], ["child1", "child2", "child3"])

  def test_codelist_indexing(self):
    code = self.create_code()
    l = code.select("child")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l), 3)
    self.assertEqual(l[0].data, "child1")
    self.assertEqual(l[1].data, "child2")
    self.assertEqual(l[2].data, "child3")

  # code iterator and indexing
  
  def test_code_len_and_iterator(self):
    code = self.create_code()
    self.assertEqual(len(code), 4)
    self.assertEqual([c.data for c in code],
                     ["child1", "child2", "child4", "child3"])

  def test_code_indexing(self):
    code = self.create_code()
    self.assertEqual(len(code), 4)
    self.assertEqual(code[0].data, "child1")
    self.assertEqual(code[1].data, "child2")
    self.assertEqual(code[2].data, "child4")
    self.assertEqual(code[3].data, "child3")

  def test_stick_codelist(self):
    code = self.create_code()
    l = code.find("b")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l), 3)
    self.assertEqual(l.codes[0].data, "child2b")
    self.assertEqual(l.codes[1].data, "child2b1")
    self.assertEqual(l.codes[2].data, "child2b2")
    self.assertFalse(l.codes[0].sticky)
    self.assertFalse(l.codes[1].sticky)
    self.assertFalse(l.codes[2].sticky)
    l2 = l.stick_top()
    self.assertIsInstance(l2, List)
    self.assertEqual(len(l2), 3)
    self.assertEqual(l2.codes[0].data, "child2b")
    self.assertEqual(l2.codes[1].data, "child2b1")
    self.assertEqual(l2.codes[2].data, "child2b2")
    # check on initial list
    self.assertTrue(l.codes[0].sticky)
    self.assertTrue(l.codes[1].sticky)
    self.assertTrue(l.codes[2].sticky)
    # check that other codes didn't get sticked, e.g. those with an "a" tag
    self.assertTrue(all([not c.sticky for c in code.find("a")]))

  def test_untstick_codelist(self):
    code = self.create_code()
    l = code.find("sticky")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l), 2)
    self.assertEqual(l.codes[0].data, "child1")
    self.assertEqual(l.codes[1].data, "child3")
    self.assertTrue(l.codes[0].sticky)
    self.assertTrue(l.codes[1].sticky)
    l2 = l.unstick()
    self.assertIsInstance(l2, List)
    self.assertEqual(len(l2), 2)
    self.assertEqual(l2.codes[0].data, "child1")
    self.assertEqual(l2.codes[1].data, "child3")
    # check on initial list
    self.assertFalse(l.codes[0].sticky)
    self.assertFalse(l.codes[1].sticky)

  def test_tag_codelist(self):
    code = self.create_code()
    l = code.find("b")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l), 3)

    self.assertFalse("taggy" in code.find("mr pink").tags)
    self.assertFalse("taggy" in code.select("*", "*", "1").tags)
    self.assertFalse("taggy" in code.select("*", "*", "2").tags)
    l.tag("taggy")
    self.assertTrue("taggy" in code.find("mr pink").tags)
    self.assertTrue("taggy" in code.select("*", "*", "1").tags)
    self.assertTrue("taggy" in code.select("*", "*", "2").tags)

  def test_untag_codelist(self):
    code = self.create_code()
    l = code.find("b")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l), 3)

    l.untag("b")
    self.assertIsNone(code.find("b"))
  
  def test_append_codelist(self):
    code = self.create_code()
    l = code.find("b")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l), 3)

    new = Code("new").tag("new")
    l.append(new)
    self.assertIs(code.select("2","b",)[2],    new)
    self.assertIs(code.select("2","b","1")[0], new)
    self.assertIs(code.select("2","b","2")[0], new)

  def test_contains_codelist(self):
    code = self.create_code()
    l = code.find("b")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l), 3)

    new = Code("new").tag("new")
    l.contains(new)
    self.assertIs(code.select("2","b",)[2],    new)
    self.assertIs(code.select("2","b","1")[0], new)
    self.assertIs(code.select("2","b","2")[0], new)

  def test_select_codelist(self):
    code = self.create_code()
    l = code.select("child").select("grandchild")
    self.assertIsInstance(l, List)
    self.assertEqual(len(l), 2)
    self.assertEqual([code.data for code in l], ["child2a","child2b"])

  def test_find_codelist(self):
    code = self.create_code()
    result = code.find("mr pink").find("2")
    self.assertIsInstance(result, Code)
    self.assertEqual(result.data, "child2b2")

    result = code.find("mr pink").find("child")
    self.assertIsInstance(result, List)

  def test_insert_codelist(self):
    code = self.create_code()
    code.find("grandchild").insert_before(code.find("c"))
    self.assertEqual("\n" + str(code),"""
something
  child1 [1,child,sticky] <sticky>
  child2 [2,child]
    child2a [a,grandchild,mr red]
    child2b [b,grandchild,mr pink]
      child2b1 [1,b,child,grand,great]
      child2b2 [2,b,child,grand,great]
    child2a [a,grandchild,mr red]
    child2b [b,grandchild,mr pink]
      child2b1 [1,b,child,grand,great]
      child2b2 [2,b,child,grand,great]
    child2c [c]
  child2a [a,grandchild,mr red]
  child2b [b,grandchild,mr pink]
    child2b1 [1,b,child,grand,great]
    child2b2 [2,b,child,grand,great]
  child4 [c]
  child3 [3,child,sticky] <sticky>""")

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestBase)
  unittest.TextTestRunner(verbosity=2).run(suite)
