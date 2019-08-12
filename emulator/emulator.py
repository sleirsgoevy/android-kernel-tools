import unicorn, ctypes

uc = unicorn.Uc(unicorn.UC_ARCH_ARM64, unicorn.UC_MODE_LITTLE_ENDIAN)
libc = ctypes.CDLL('libc.so.6')
libc.syscall.restype = ctypes.c_ulonglong

def read_kmem_page(addr):
    buf = ctypes.create_string_buffer(4096)
    ans = libc.syscall(104, ctypes.c_void_p(1), ctypes.c_void_p(addr), buf)
    assert ans == 1507, ans
    return bytes(buf)

def get_mrs():
    buf = (ctypes.c_ulonglong*2)()
    ans = libc.syscall(104, ctypes.c_void_p(4), ctypes.c_void_p(0), buf)
    assert ans == 1510, ans
    return tuple(buf)

kpages = set()

def hook_mem(uc, acc, addr, sz, val, usr):
    if acc in (unicorn.UC_MEM_READ_UNMAPPED, unicorn.UC_MEM_WRITE_UNMAPPED, unicorn.UC_MEM_FETCH_UNMAPPED) and addr >= 0x100000000:
        print('will load page at', hex(addr))
        addr &= -4096
        print('page #'+hex(addr))
#       input()
        kpages.add(addr)
        uc.mem_map(addr, 4096, unicorn.UC_PROT_ALL)
        uc.mem_write(addr, read_kmem_page(addr))
        return True
    elif uc.reg_read(unicorn.arm64_const.UC_ARM64_REG_PC) == 0xf0000 + len(emu_launch) - 4:
        hook_mem.emu_ok = True
        return False
    else:
        print('wtf?', acc, hex(addr), hex(uc.reg_read(unicorn.arm64_const.UC_ARM64_REG_PC)))
        return False

def unload_kpages():
    while True:
        try: i = kpages.pop()
        except KeyError: break
        uc.mem_unmap(i, 4096)

def hook_code(uc, addr, sz, usr):
    if hook_code.just_called:
        hook_code.just_called = False
        print('[trace] call to', hex(addr))
    print('[trace]', hex(addr))
    instr = uc.mem_read(addr, sz)
    if len(instr) >= 4 and (instr[3] & 0xfc) == 0x94:
        hook_code.just_called = True
    elif len(instr) >= 4 and instr[3] == 0xd6 and (instr[1] & 0xfc) == (instr[0] & 0x1f) == 0:
        if instr[2] == 0x3f:
            hook_code.just_called = True
        elif instr[2] == 0x5f:
            print('[trace] return')

uc.hook_add(unicorn.UC_HOOK_MEM_READ_UNMAPPED | unicorn.UC_HOOK_MEM_WRITE_UNMAPPED | unicorn.UC_HOOK_MEM_FETCH_UNMAPPED, hook_mem)
uc.hook_add(unicorn.UC_HOOK_CODE, hook_code)
uc.mem_map(0x100000, 0x3ff00000, unicorn.UC_PROT_READ | unicorn.UC_PROT_WRITE)
uc.mem_map(0xf0000, 0x10000, unicorn.UC_PROT_READ | unicorn.UC_PROT_EXEC)

with open('emu_launch.bin', 'rb') as file:
    emu_launch = file.read()
uc.mem_write(0xf0000, emu_launch)

def emulate(entry, p1, p2, p3, p4):
    sp_el0, tpidr_el1 = get_mrs()
    uc.reg_write(unicorn.arm64_const.UC_ARM64_REG_SP, 0x40000000)
    uc.reg_write(unicorn.arm64_const.UC_ARM64_REG_X0, p1)
    uc.reg_write(unicorn.arm64_const.UC_ARM64_REG_X1, p2)
    uc.reg_write(unicorn.arm64_const.UC_ARM64_REG_X2, p3)
    uc.reg_write(unicorn.arm64_const.UC_ARM64_REG_X3, p4)
    uc.reg_write(unicorn.arm64_const.UC_ARM64_REG_X4, sp_el0)
    uc.reg_write(unicorn.arm64_const.UC_ARM64_REG_X5, tpidr_el1)
    uc.reg_write(unicorn.arm64_const.UC_ARM64_REG_X6, entry)
    hook_mem.emu_ok = False
    hook_code.just_called = True
    try: uc.emu_start(0xf0000, 0xf0000 + len(emu_launch))
    except:
        if not hook_mem.emu_ok: raise
    unload_kpages()
    return uc.reg_read(unicorn.arm64_const.UC_ARM64_REG_X0)
