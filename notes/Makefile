OPT        = s
CSTANDARD  = -std=gnu99

CFLAGS     = -O$(OPT)
CFLAGS    += -funsigned-char -fpack-struct -fshort-enums
CFLAGS    += -Wall -Wstrict-prototypes
CFLAGS    += $(CSTANDARD)

ALL_CFLAGS = $(CFLAGS)

CC         = gcc

APP        = inline

all: clean run
	
run: $(APP).out
	./$<

%.out: %.c
	$(CC) $(ALL_CFLAGS) $< -o $@

clean:
	rm -f $(APP).out
