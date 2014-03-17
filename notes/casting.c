/*
 * Stand-alone experiments for design of emitted C code for typical specific
 * C-language issues
 * author: Christophe VG
 */

#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
#include <time.h>

#include "../../../../an-avr-lib/bool.h"

typedef union conv2bytes {
  float   float_value;
  int     int_value;
  uint8_t bytes[4];
} conv2bytes;

void test_convert_float(void) {
  float value = 0.25;
  union { float f; uint8_t b[sizeof(float)]; } conv = { .f = value };

  printf("float %f in bytes = %02X %02X %02X %02X\n",
          conv.f, conv.b[0], conv.b[1], conv.b[2], conv.b[3]);
  assert(conv.b[0] == 0x00);
  assert(conv.b[1] == 0x00);
  assert(conv.b[2] == 0x80);
  assert(conv.b[3] == 0x3E);
}

int main(void) {
  printf("sizeof(float)=%lu\n", sizeof(float));
  printf("sizeof(int)=%lu\n", sizeof(int));

  test_convert_float();

  exit(EXIT_SUCCESS);
}