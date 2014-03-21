// extending stdarg with a marco to copy a variable list of arguments to an
// array
// author: Christophe VG

#include <stdarg.h>

#define va_collect(buffer, size, type)\
va_list ap; \
va_start(ap, size); \
for(int i=size; i>0; i--) { buffer[size-i] = (type)va_arg(ap, int); } \
va_end(ap);
