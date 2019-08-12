# payload/

This directory contains a kernel memory read/write payload to be loaded by the patch in `/patch`.

All the provided files (i.e. loader and all payloads) can be built by typing `make`.

# loader.c

`usage: ./loader <payload>`

Loads the given payload file using the backdoor in `/patch`. This is intended to be run on the device.

More specifically, it does the following.
1. `mmap` 64KB of memory and read the payload into that area.
2. Invoke syscall #104 (from the patch, originally `__NR_kexec`) with that address as an argument.
3. The patch loads the payload into kernel memory, sets the memory permissions to `rwx` and passes control to it.
4. Print the syscall's return value (actually returned from the payload).

# test.c

`usage: ./loader test`

A simple test payload which returns `12345ll`. Intended to verify that the setup is correct.

# mem_io.c

`usage: ./loader mem_io`

A payload that provides arbitrary kmem read/write primitives.
** Note: this payload doesn't implement any kind of locking, i.e. is not thread-safe. **

This payload replaces syscall #104 with its own handler. Its api is described below.

`unsigned long long syscall(104, unsigned long long cmd, void* param1, void* param2)`

The behaviour of this syscall depends on the value of `cmd`:
* `cmd == 1`: copy 4096 bytes from kernel address `param1` to user address `param2`. Returns `1507ll` on success, panics on failure. The kernel address `param1` must have the read bit enabled.
* `cmd == 2`: copy 4096 bytes from user address to `param2` to kernel address `param1`. Returns `1508ll` on success, panics on failure. The kernel address `param1` must have the write bit enabled.
* `cmd == 3`: restore the original syscall handler. Returns `1509ll`.
* `cmd == 4`: writes the following structure

```
struct
{
    unsigned long long reg__sp_el0;
    unsigned long long reg__tpidr_el1;
};
```

to user address `param2`. `param1` is ignored. The structure fields are filled from the appropriate CPU registers.

Returns `1510ll` on success, panics on failure.

If the `cmd` value is unsupported, the syscall handler returns `-38` (i.e. `-ENOSYS`).

# mem_io_disable.py

`usage: python3 mem_io_disable.py`

This script invokes `syscall(104, 3)` to disable the `mem_io` payload.

# make.sh

This file should be used to build custom payloads.

`usage: bash make.sh <payload>`

Builds the source in `<payload>.c` into a ready-to-load payload in `<payload>`. This script must be called from the `/payload` directory.

# linux.hh

This file allows payload developers to use functions from the Linux kernel. Its format is the same as of any C header, however, all lines containing `linux_` are treated specifically.

Example:

```
int linux_sys_getpid();
void* linux_sys_call_table[];
```

The script `linuxhh.py` (`python3 linuxhh.py`) compiles `linux.hh` into ready-to-include `linux.h`, using symbols in `/patch/kallsyms`.
