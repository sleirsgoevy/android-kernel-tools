aarch64-linux-gnu-gcc "$1.c" -c -o "$1.o"
objcopy -G _start "$1.o"
aarch64-linux-gnu-gcc "$1.o" -shared -o "$1.elf"
python3 elf2sh.py "$1.elf" "$1"
