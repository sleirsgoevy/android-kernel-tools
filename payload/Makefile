all: test mem_io loader

clean:
	rm test mem_io loader *.o *.elf *.bin linux.h || true

linux.h: linux.hh ../patch/kallsyms
	python3 linuxhh.py

prologue.o: prologue.s
	aarch64-linux-gnu-gcc -c prologue.s -o prologue.o

prologue.bin: prologue.o
	objcopy --dump-section .text=prologue.bin prologue.o

_make_ready: linux.h prologue.bin

test: test.c _make_ready
	bash make.sh test

mem_io: mem_io.c _make_ready
	bash make.sh mem_io

loader: loader.c
	aarch64-linux-gnu-gcc loader.c -o loader
