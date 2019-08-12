.global _start

_start:
msr sp_el0, x4
msr tpidr_el1, x5
blr x6
mov x5, #0
ldr x5, [x5]
