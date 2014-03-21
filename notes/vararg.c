/*
 * Stand-alone experiments for design of emitted C code for typical specific
 * C-language issues
 * author: Christophe VG
 */

#include <stdlib.h>
#include <stdio.h>

#include "stdarg-collect.h"

void print(int size, ...) {
  uint8_t* buffer = malloc(size + 1 * sizeof(uint8_t));
  va_collect(buffer, size, uint8_t)
  buffer[size] = '\0';
  printf("%s\n", buffer);
}

int main(void) {
  print(5, 'a', 'b', 'c', 'd', 'e');
  exit(EXIT_SUCCESS);
}
