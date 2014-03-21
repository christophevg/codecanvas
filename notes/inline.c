/*
 * Stand-alone experiments for design of emitted C code for typical CodeCanvas
 * constructs, like tuples, list of ..., matchers, ...
 * author: Christophe VG
 */

#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <time.h>

#include "../../../../platforms/moose/bool.h"

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
  node_t* node = malloc(sizeof(node_t));
  node->queue = NULL;
  return node;
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
bool match_4(void* in) {
  int value = *(int*)in;
  return value == 4;
}

bool match_5(void* in) {
  int value = *(int*)in;
  return value == 5;
}

bool match_6(void* in) {
  int value = *(int*)in;
  return value == 6;
}

bool match_7(void* in) {
  int value = *(int*)in;
  return value == 7;
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

bool list_of_tuple_0s_contains_with_for(tuple_0_t* iter, matcher_t elem_0_matcher,
                                                         matcher_t elem_1_matcher)
{
  for(;iter != NULL; iter = iter->next) {
    if( elem_0_matcher((void*)&(iter->elem_0)) && 
        elem_1_matcher((void*)&(iter->elem_1)) )
    {
      return TRUE;
    }
  }
  return FALSE;
}                                                   

bool list_of_tuple_0s_contains_inlined_match_5_match_anything(tuple_0_t* iter) {
  while(iter != NULL) {
    if( iter->elem_0 == 5) {
      return TRUE;
    }
    iter = iter->next;
  }
  return FALSE;
}                                                   

// removing uses matchers to determine which items to remove from the list
int list_of_tuple_0s_remove(tuple_0_t** list, matcher_t elem_0_matcher,
                                               matcher_t elem_1_matcher)
{
  int removed = 0;  // count the number of removed nodes

  tuple_0_t *iter;  // iterator through list
  tuple_0_t *prev;  // cached reference to previous node

  for(iter = *list, prev = NULL; iter != NULL;	prev = iter, iter = iter->next) {
    if( elem_0_matcher((void*)&(iter->elem_0)) && 
        elem_1_matcher((void*)&(iter->elem_1)) )
    {
      if(prev == NULL) {   // we need to remove the head
        *list = iter->next;
      } else {
        prev->next = iter->next;
      }
      free(iter);
      removed++;
    }
  }

  return removed;
}

int list_of_tuple_0s_remove_inlined_match_6_match_anything(tuple_0_t** list) {
  int removed = 0;  // count the number of removed nodes

  tuple_0_t* iter = *list;  // iterator through list
  tuple_0_t* prev = NULL;  // cached reference to previous node
  
  while(iter != NULL) {
    if( iter->elem_0 == 6 && TRUE ) {
      if(prev == NULL) {   // we need to remove the head
        *list = iter->next;
      } else {
        prev->next = iter->next;
      }
      free(iter);
      removed++;
    }
  	prev = iter;
    iter = iter->next;
  }

  return removed;
}

bool list_of_bytes_contains_match_eq_0x00_match_eq_0x02(uint8_t *list,
                                                        uint16_t length)
{
  for(;length>1;length--, list++) {
    if( *list == 0x00 && *(list+1) == 0x02 ) {
      return TRUE;
    }
  }
  return FALSE;
}

int main(void) {
  node_t* node = nodes_create();

#define occurences 100
  int c;

  for(c=0; c<occurences; c++) {
    tuple_0_t* item = tuple_0s_create();
    item->elem_0 = 4;
    item->elem_1 = malloc(4 * sizeof(uint8_t));
    item->elem_1[0] = 123;
    item->elem_1[1] = 124;
    item->elem_1[2] = 125;
    item->elem_1[3] = '\0';

    list_of_tuple_0s_push(&node->queue, item);
  }

  // add one item with value 5 at the end
  tuple_0_t* item5 = tuple_0s_create();
  item5->elem_0 = 5;
  item5->elem_1 = malloc(5 * sizeof(uint8_t));
  item5->elem_1[0] = 223;
  item5->elem_1[1] = 224;
  item5->elem_1[2] = 225;
  item5->elem_1[3] = 226;
  item5->elem_1[4] = '\0';

  list_of_tuple_0s_push(&node->queue, item5);

  // add one item with value 5 at the end
  tuple_0_t* item6 = tuple_0s_create();
  item6->elem_0 = 6;
  item6->elem_1 = malloc(3 * sizeof(uint8_t));
  item6->elem_1[0] = 23;
  item6->elem_1[1] = 24;
  item6->elem_1[2] = '\0';

  list_of_tuple_0s_push(&node->queue, item6);
  
  assert(list_of_tuple_0s_contains(node->queue, match_5, match_anything));
  assert(list_of_tuple_0s_contains_with_for(node->queue, match_5, match_anything));
  assert(list_of_tuple_0s_contains_inlined_match_5_match_anything(node->queue));
  
  // measure time of different contains implementations
  int  l;
  long i;
  
#define iterations 1
#define loops      1000000

  clock_t tic, toc;
  
  printf("performing %d iterations of %d loops\n", iterations, loops);

  for(l=0; l<iterations; l++) {

    printf("iteration %d:\n", l);

    tic = clock();
    for(i=0;i<loops;i++) {
      list_of_tuple_0s_contains(node->queue, match_5, match_anything);
    }
    toc = clock();
    printf("while loop: %f seconds\n", (double)(toc - tic) / CLOCKS_PER_SEC);
    
    tic = clock();
    for(i=0;i<loops;i++) {
      list_of_tuple_0s_contains_with_for(node->queue, match_5, match_anything);
    }
    toc = clock();
    printf("for loop  : %f seconds\n", (double)(toc - tic) / CLOCKS_PER_SEC);

    tic = clock();
    for(i=0;i<loops;i++) {
      list_of_tuple_0s_contains_inlined_match_5_match_anything(node->queue);
    }
    toc = clock();
    printf("inlined   : %f seconds\n", (double)(toc - tic) / CLOCKS_PER_SEC);

    printf("\n");
  }

  assert(list_of_tuple_0s_remove(&node->queue, match_5, match_anything) == 1);
  assert(list_of_tuple_0s_remove(&node->queue, match_5, match_anything) == 0);
  assert(list_of_tuple_0s_remove_inlined_match_6_match_anything(&node->queue) == 1);
  assert(list_of_tuple_0s_remove_inlined_match_6_match_anything(&node->queue) == 0);

  // list of bytes
  
  uint8_t* list = malloc(5 * sizeof(uint8_t));
  list[0] = 0x15;
  list[1] = 0x20;
  list[2] = 0x00;
  list[3] = 0x02;
  list[4] = 0x12;

  assert(list_of_bytes_contains_match_eq_0x00_match_eq_0x02(list, 5));

  list[2] = 0x13;
  list[3] = 0x14;

  assert(list_of_bytes_contains_match_eq_0x00_match_eq_0x02(list, 5) == FALSE);

  list[4] = 0x00;

  assert(list_of_bytes_contains_match_eq_0x00_match_eq_0x02(list, 5) == FALSE);

  list[3] = 0x00;
  list[4] = 0x02;

  assert(list_of_bytes_contains_match_eq_0x00_match_eq_0x02(list, 5));

  return EXIT_SUCCESS;
}
