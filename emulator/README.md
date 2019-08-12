# emulator/

This directory contains a [Unicorn](https://unicorn-engine.org)-based emulator that emulates a given syscall in userspace, using the `mem_io` payload (see `/payload/mem_io.c`) to read kernel memory.

All memory accesses performed by the emulator are read-only, to prevent kernel memory corruption in case of an emulator bug or a race condition.

See `emulator.py` for details.
