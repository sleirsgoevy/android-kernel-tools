import sys

symbols = {}

with open('kallsyms') as file:
    base_addr, _, symbol = file.readline().split(' ', 2)
    symbols[symbol.strip()] = 0
    base_addr = int(base_addr, 16)
    for i in file:
        addr, _, symbol = i.split(' ', 2)
        symbols[symbol.strip()] = int(addr, 16) - base_addr

symbols_set = set(symbols.values())

with open('kernel', 'rb') as file: kernel = bytearray(file.read())

instructions = {}

with open('kernel.dump') as file:
    kd_lines = list(file)

try:
    with open('instr_pool.dump') as file:
        kd_lines.extend(file)
except IOError: pass

for line in kd_lines:
    line = line.split(';', 1)[0].split('//', 1)[0].split()
    if not line or line[0][-1:] != ':': continue
    try: addr = int(line[0][:-1], 16)
    except ValueError: continue
    binrepr = int(line[1], 16).to_bytes(len(line[1]) // 2, 'little')
    instr = ' '.join(line[2:])
    instructions[instr] = binrepr

def resolve_symbol(sym):
    try: sym = int(sym, 16)
    except ValueError:
        off = 0
        if '+' in sym:
            sym, off = sym.split('+', 1)
            off = eval(off)
        sym = symbols[sym.strip()] + off
    return sym

def parse_command(infile):
    for l in infile:
        l = l.split('#', 1)[0] + ' '
        if not l.isspace(): break
    else: return False
    assert l.startswith('at ')
    l0 = l
    sym = resolve_symbol(l[3:])
    binrepr = b''
    syms_allowed = True
    check_same = False
    for l in infile:
        l = l.split(';', 1)[0]
        if (l+' ').isspace(): break
        instr = ' '.join(l.split())
        if instr.startswith('.byte '):
            binrepr += bytes(eval('('+instr[6:]+')'))
        elif instr.startswith('.ptr '):
            binrepr += (resolve_symbol(instr[5:])+base_addr).to_bytes(8, 'little')
        elif instr.startswith('.bl '):
            sym2 = resolve_symbol(instr[4:])
            off = sym2 - (sym + len(binrepr))
            assert (off & 3) == 0 and off in range(-0x8000000, 0x8000000), "invalid bl"
            binrepr += (0x94000000|((off>>2)&0x1ffffff)).to_bytes(4, 'little')
        elif instr == '.nosyms':
            syms_allowed = False
        elif instr == '.assert':
            check_same = True
        else:
            binrepr += instructions[instr]
    for i in range(sym + 1, sym + len(binrepr)):
        assert i not in symbols_set or syms_allowed, (l0[3:].strip()+' crosses another symbol (%d byte cross)'%(sym + len(binrepr) - i))
    if check_same:
        assert kernel[sym:sym+len(binrepr)] == binrepr, l0[3:].strip()
    else:
        kernel[sym:sym+len(binrepr)] = binrepr
    return True

with open(sys.argv[1]) as infile:
    while parse_command(infile): pass

with open('kernel.mod', 'wb') as file: file.write(kernel)
