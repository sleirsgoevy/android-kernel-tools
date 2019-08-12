#include <unistd.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <sys/mman.h>
#include <stdio.h>

int main(int argc, const char** argv)
{
    if(argc != 2)
    {
        fprintf(stderr, "usage: %s <payload>\n", argv[0]);
        return 1;
    }
    int fd = open(argv[1], O_RDONLY);
    if(fd < 0)
    {
        perror("open");
        return 1;
    }
    long long sz = lseek(fd, 0, SEEK_END);
    if(sz < 0)
    {
        perror("lseek");
        return 1;
    }
    if(sz > 0x10000)
    {
        fprintf(stderr, "error: payload size is larger than 65536 bytes\n");
        return 1;
    }
    if(lseek(fd, 0, SEEK_SET) < 0)
    {
        perror("lseek");
        return 1;
    }
    void* addr = mmap(NULL, 0x10000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if(addr == (void*)-1)
    {
        perror("mmap");
        return 1;
    }
    if(read(fd, addr, sz) != sz)
    {
        perror("read");
        return 1;
    }
    close(fd);
    long long result = syscall(104, addr);
    printf("%llx (%lld)\n", result, result);
    return 0;
}
