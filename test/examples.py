# examples.py
# tests CodeCanvas functionality
# author: Christophe VG

import unittest

from codecanvas.base       import Code, List, Canvas
from codecanvas.structure  import Unit, Module

import codecanvas.instructions as code
import codecanvas.languages.C  as C

class TestExamples(unittest.TestCase):
  
  def test_readme_canvas(self):
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

  def test_readme_generation(self):
    # create a compilation unit with one module, called "hello"
    unit   = Unit()
    module = unit.append( Module("hello") )

    # create a main function
    main = unit.select("hello", "dec").append(code.Function(name="main"))

    # add a print statement to the main function
    main.append(code.Print("Hello World\n"))

    self.assertEqual("\n" + str(unit), """
Module hello [hello]
  Section def [def]
  Section dec [dec]
    Function {'params': [], 'type': void, 'id': main}
      Print {'args': (), 'string': "Hello World\\n"}""")

    # Generate the code of the main function
    self.assertEqual("\n" + C.Emitter().emit(unit), """
#include <stdio.h>
void main(void) {
printf("Hello World\\n");
}""")

    #C.Emitter().output_to("output").emit(unit)

if __name__ == '__main__':
  suite = unittest.TestLoader().loadTestsFromTestCase(TestExamples)
  unittest.TextTestRunner(verbosity=2).run(suite)
