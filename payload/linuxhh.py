import os.path

symbols = {}

with open(os.path.join(os.path.split(__file__)[0], '..', 'patch', 'kallsyms')) as file:
    for line in file:
        a, b, c = line.split()
        symbols[c] = int(a, 16)

with open('linux.hh') as infile:
    with open('linux.h', 'w') as outfile:
        lines = infile.read().split(';')
        assert (lines.pop()+' ').isspace()
        for line in lines:
            line = line.strip().replace('\n', ' ')
            if 'linux_' not in line:
                outfile.write(line+';\n')
                continue
            assert line.count('linux_') == 1
            i = i0 = line.find('linux_')
            while i < len(line) and (line[i].isalnum() or line[i] == '_'): i += 1
            sym = line[i0+6:i]
            ptr_type = '('+line[:i0]+'(*volatile)'+line[i:]+')'
            line1 = '#define linux_'+sym+' (*('+ptr_type+hex(symbols[sym])+'ll))\n'
            outfile.write(line1)
