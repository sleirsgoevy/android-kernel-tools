# patch/

This directory contains the `apply_patch.py` script and related files.

To import a kernel do the following:
1. Unpack the `boot.img` and place the `kernel` file into this directory
2. Run the `import_kernel.sh` script to create `kernel.o` and `kernel.dump`
3. Place the `kallsyms` file into this directory (e.g. `adb pull /proc/kallsyms .`)

## apply_patch.py

`usage: python3 apply_patch.py <patch_file>`

Applies the given patch and dumps the patched kernel into `kernel.mod`.

## callgraph.py

`usage: python3 callgraph.py [function] [-r] [-q <func>]...`

If called without arguments, parse the callgraph and dump it into `callgraph.json`.
If called with an argument, pretty-print the call graph of the specified function.
See the source for more details.

## patch-kexec.txt

This patch replaces the `kexec` syscall with a function that copies 64KB of user memory into the kernel space and executes it. See `/payload/README.md` for more details.
