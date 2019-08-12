objcopy -I binary kernel -O elf64-littleaarch64 -B aarch64 kernel.o
objdump -D kernel.o > kernel.dump
