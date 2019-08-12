.global _start

_start:
add sp, sp, #0x10
ldp x0, x1, [sp]
add sp, sp, #0x10
ldr x30, [sp]
add sp, sp, #0x10
