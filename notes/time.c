/*
 * Stand-alone experiments for design of emitted C code for typical specific
 * C-language issues, in this case clock and usleep.
 * author: Christophe VG
 */

#include <stdlib.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/time.h>

time_t my_clock(void) {
  struct timeval  tp;
  struct timezone tzp = { .tz_minuteswest = 0, .tz_dsttime     = 0 };
  gettimeofday(&tp, &tzp);
  return tp.tv_sec * 1000 + (tp.tv_usec/1000);
}

int main(void) {
  usleep(2000*1000);

  time_t start = my_clock();
  usleep(300*1000);
  time_t end = my_clock();

  printf("elapsed: %lu\n", end-start);

  exit(EXIT_SUCCESS);
}