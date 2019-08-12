import os, sys, shlex, subprocess

data = os.popen('nm '+shlex.quote(sys.argv[1])).read()

addr = None

for i in data.split('\n'):
    if i.endswith(' T _start'):
        addr = int(i[:-9], 16)

if addr == None:
    print('Warning: symbol `_start` not found')
    addr = 0

with open(sys.argv[1], 'rb') as file: data = file.read()

with open('prologue.bin', 'rb') as file:
    prologue = file.read()

prologue += (((addr - len(prologue))>>2)|0x14000000).to_bytes(4, 'little')
data = prologue + data[len(prologue):]

with open(sys.argv[2], 'wb') as file: file.write(data)
