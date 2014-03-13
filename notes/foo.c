/*
 * Stand-alone experiments for design of emitted C code for typical CodeCanvas
 * constructs, like tuples, list of ..., matchers, ...
 * author: Christophe VG
 */

#include <stdlib.h>
#include <stdio.h>
#include <assert.h>

typedef uint8_t bool;
#define TRUE  1
#define FALSE 0

// tuple as a struct with additional self referencing next pointer in case that
// it is used in a 

typedef struct tuple_0_t {
  int elem_0;
  uint8_t* elem_1;
  struct tuple_0_t* next;       // added when tuple is used as a list
} tuple_0_t;

// example of typical "node" container of a list of the above tuple

typedef struct {
  tuple_0_t* queue;
} node_t;

// constructor for nodes
node_t* nodes_create(void) {
  return malloc(sizeof(node_t));
}

// constructor for tuple
tuple_0_t* tuple_0s_create(void) {
  return malloc(sizeof(tuple_0_t));
}

// push implementation, abuses option to push back the listed items to minimize
// the effort to add both in complexity and in code size ;-)
void list_of_tuple_0s_push(tuple_0_t** list, tuple_0_t* item) {
  item->next = *list;
  *list      = item;
}

// matchers are function pointers to functions that accept values are return a
// boolean indicating if the value matches the implemented constraints.
// because we don't know what arguments will be given, we pass data around 
// through void*.
typedef bool(*matcher_t)(void*);

// as an example, we can implement match_anything. it doesn't do anything with
// respect to arguments and thus simply ignores them, but we need to accept at
// least one, because the caller doesn't know that this is a static matcher and
// will pass in its argument as a void*
bool match_anything(void* dummy) {
  return TRUE;
}

// we can also implement one that does use the arguments. all arguments are
// passed as void*
// let's say that this matcher checks for 
bool match_0(void* in) {
  int value = *(int*)(in);
  return value < 5;
}

bool list_of_tuple_0s_contains(tuple_0_t* iter, matcher_t elem_0_matcher,
                                                matcher_t elem_1_matcher)
{
  while(iter != NULL) {
    if( elem_0_matcher((void*)&(iter->elem_0)) && 
        elem_1_matcher((void*)&(iter->elem_1)) )
    {
      return TRUE;
    }
    iter = iter->next;
  }
  return FALSE;
}                                                   

// removing uses matchers to determine which items to remove from the list
void list_of_tuple_0s_remove(tuple_0_t** list, matcher_t elem_0_matcher,
                                               matcher_t elem_1_matcher)
{
  tuple_0_t* iter = *list;
  // TODO: boundary checks,...
  // TODO: remove from linked list, itereated by iter when
  if( elem_0_matcher((void*)&(iter->elem_0)) && 
      elem_1_matcher((void*)&(iter->elem_1)) )
  {
    // remove
  } 
}

int main(void) {
  node_t* node = nodes_create();

  tuple_0_t* item1 = tuple_0s_create();
  item1->elem_0 = 4;
  item1->elem_1 = malloc(4 * sizeof(uint8_t));
  item1->elem_1[0] = 123;
  item1->elem_1[1] = 124;
  item1->elem_1[2] = 125;
  item1->elem_1[3] = '\0';

  tuple_0_t* item2 = tuple_0s_create();
  item2->elem_0 = 5;
  item2->elem_1 = malloc(5 * sizeof(uint8_t));
  item2->elem_1[0] = 223;
  item2->elem_1[1] = 224;
  item2->elem_1[2] = 225;
  item2->elem_1[3] = 226;
  item2->elem_1[3] = '\0';

  tuple_0_t* item3 = tuple_0s_create();
  item3->elem_0 = 6;
  item3->elem_1 = malloc(3 * sizeof(uint8_t));
  item3->elem_1[0] = 1;
  item3->elem_1[1] = 2;
  item3->elem_1[2] = 3;
  item3->elem_1[3] = 4;
  item3->elem_1[3] = '\0';
  
  list_of_tuple_0s_push(&node->queue, item1);
  list_of_tuple_0s_push(&node->queue, item2);
  list_of_tuple_0s_push(&node->queue, item3);
  
  assert(node->queue->elem_0             == 6);
  assert(node->queue->next->elem_0       == 5);
  assert(node->queue->next->next->elem_0 == 4);
  
  assert(list_of_tuple_0s_contains(node->queue, match_0, match_anything));
  
  return EXIT_SUCCESS;
}
