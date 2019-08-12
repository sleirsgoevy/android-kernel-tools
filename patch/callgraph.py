import sys, collections, json

symbols = {}
symbols2 = collections.defaultdict(list)

with open('kallsyms') as file:
    base_addr, _, symbol = file.readline().split(' ', 2)
    symbols[symbol.strip()] = 0
    base_addr = int(base_addr, 16)
    for i in file:
        addr, _, symbol = i.split(' ', 2)
        symbols[symbol.strip()] = int(addr, 16) - base_addr
        symbols2[int(addr, 16) - base_addr].append(symbol.strip())

if len(sys.argv) > 1:
    sym = sys.argv[1]
    with open('callgraph.json') as file:
        callgraph = json.load(file)
    stack = set()
    def do_print(sym, t='', silent=False):
        for i in callgraph.get(sym, []):
            silent2 = silent or '--skip='+i[1] in sys.argv
            if not silent2:
                print('BASE+0x%%x\t%s%%s'%t%tuple(i))
            if '-r' in sys.argv and i[1] not in stack:
                stack.add(i[1])
                do_print(i[1], t+'  ', silent2)
                if '-q' not in sys.argv: stack.remove(i[1])
    do_print(sym)
    exit(0)

curr_sym = ["<anonymous>"]
callgraph = collections.defaultdict(list)

with open('kernel.dump') as file:
    for line in file:
        line = line.split(';', 1)[0].split('//', 1)[0].split()
        if not line or line[0][-1:] != ':': continue
        try: addr = int(line[0][:-1], 16)
        except ValueError: continue
        instr = ' '.join(line[2:]).strip()
        if addr in symbols2:
            curr_sym = symbols2[addr]
        elif instr.split()[0] == 'bl':
            addr2 = int(instr.split()[1], 16)
            for i in curr_sym:
                if addr2 in symbols2:
                    callgraph[i].append((addr, symbols2[addr2][0]))
                else:
                    callgraph[i].append((addr, "<func%x>"%(base_addr+addr2)))

with open('callgraph.json', 'w') as file:
    file.write(json.dumps(callgraph))
