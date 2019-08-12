# android-kernel-tools

This repository contains various tools that enable inspection and modification of an Android kernel without source code. These tools currently only work for ARM64 (a.k.a. aarch64) kernels.

Subdirectories:
* `patch/` - kernel binary patch tool & a shellcode injection patch; see `patch/README.md`
* `payload/` - payloads to be injected into a running kernel + build scripts to build a custom one; see `payload/README.md`
* `emulator/` - a Unicorn-based script capable of emulating parts of the running kernel; see `emulator/README.md`
