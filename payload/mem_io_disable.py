import ctypes

libc = ctypes.CDLL('libc.so.6')

ans = libc.syscall(104, ctypes.c_void_p(3))
assert ans == 1509, ans
