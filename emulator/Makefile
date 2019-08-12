all: emu_launch.bin

emu_launch.o: emu_launch.s
	aarch64-linux-gnu-gcc emu_launch.s -c -o emu_launch.o

emu_launch.bin: emu_launch.o
	objcopy --dump-section .text=emu_launch.bin emu_launch.o

clean:
	rm emu_launch.bin
