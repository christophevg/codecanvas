/*
 * Stand-alone experiments for design of emitted C code.
 * - creation and freeing of data inside tuples
 * - handling of payload_t
 * author: Christophe VG
 */

#include <stdlib.h>
#include <stdio.h>
#include <malloc/malloc.h>
#include <string.h>

typedef struct payload_t {
  int size;
  uint8_t* data;
} payload_t;

payload_t* make_payload(uint8_t* data, int size) {
  payload_t* payload = malloc(sizeof(payload_t));
  payload->size = size;
  payload->data = malloc(size*sizeof(uint8_t));
  memcpy(payload->data, data, size);
  return payload;
}

payload_t* copy_payload(payload_t* source) {
  payload_t* copy = malloc(sizeof(payload_t));
  copy->data = malloc(source->size * sizeof(uint8_t));
  memcpy(copy->data, source->data, source->size);
  return copy;
}

void free_payload(payload_t* payload) {
  free(payload->data);
  free(payload);
}

typedef struct tuple_t {
  int something;
  payload_t* payload;
} tuple_t;

tuple_t* make_tuple(int something, payload_t* payload) {
  tuple_t *tuple = malloc(sizeof(tuple_t));
  tuple->something = something;
  tuple->payload = copy_payload(payload);
  return tuple;
}

void free_tuple(tuple_t* tuple) {
  free_payload(tuple->payload);
  free(tuple);
}

int main(void) {

  uint8_t* data = malloc(1024*sizeof(uint8_t));
  data[1023] = 0x20;
  
  payload_t* payload = make_payload(data, 1024);

  printf("data    : %lu\n", malloc_size(data));               // 1024
  free(data);
  printf("data    : %lu\n", malloc_size(data));               // 0
  
  tuple_t* tuple1 = make_tuple(1, payload);

  printf("data    : %lu\n", malloc_size(data));               // 1024 ??
  printf("\n");

  tuple_t* tuple2 = make_tuple(2, payload);

  printf("data    : %lu\n", malloc_size(data));               // 1024 ??
  printf("payload : %lu\n", malloc_size(payload->data));
  printf("tuple1  : %lu\n", malloc_size(tuple1->payload->data));
  printf("tuple2  : %lu\n", malloc_size(tuple2->payload->data));
  printf("\n");

  free_payload(payload);

  printf("data    : %lu\n", malloc_size(data));               // 1024 ??
  printf("payload : %lu\n", malloc_size(payload->data));
  printf("tuple1  : %lu\n", malloc_size(tuple1->payload->data));
  printf("tuple2  : %lu\n", malloc_size(tuple2->payload->data));
  printf("\n");

  free_tuple(tuple1);

  printf("data    : %lu\n", malloc_size(data));               // 0 !!!
  printf("payload : %lu\n", malloc_size(payload->data));
  printf("tuple1  : %lu\n", malloc_size(tuple1->payload->data));
  printf("tuple2  : %lu\n", malloc_size(tuple2->payload->data));
  printf("\n");

  free_tuple(tuple2);

  printf("data    : %lu\n", malloc_size(data));
  printf("payload : %lu\n", malloc_size(payload->data));
  printf("tuple1  : %lu\n", malloc_size(tuple1->payload->data));
  printf("tuple2  : %lu\n", malloc_size(tuple2->payload->data));
  printf("\n");

  exit(EXIT_SUCCESS);
}
