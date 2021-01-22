import sys,ctypes
from ctypes import *

KERNEL32 = windll.kernel32

def dllinject(dllpath, pid):
    ret = False
    PROCESS_ALL_ACCESS =  (0x000F0000|0x00100000|0xFFF)
    proc_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, None, pid)

    if proc_handle is not None:
        MEM_COMMIT = 0x00001000
        MEM_RESERVE = 0x00002000
        PAGE_EXECUTE_READWRITE = 0x40
        temp_buffer = bytearray()+ctypes.create_string_buffer(dllpath).raw
        alloc_address = ctypes.windll.kernel32.VirtualAllocEx(proc_handle, None,
                                                              len(temp_buffer), MEM_RESERVE|MEM_COMMIT,
                                                              PAGE_EXECUTE_READWRITE)
        if alloc_address is not None:
            c_buffer = (ctypes.c_char * len(temp_buffer)).from_buffer(temp_buffer)
            if ctypes.windll.kernel32.WriteProcessMemory(proc_handle, alloc_address, c_buffer, len(temp_buffer), None):
                import win32api
                h_kernel32=win32api.GetModuleHandle('kernel32.dll')
                h_loadlib =win32api.GetProcAddress(h_kernel32, 'LoadLibraryA')
                thread = ctypes.windll.kernel32.CreateRemoteThread(proc_handle, None, 0,h_loadlib,alloc_address,  0, None)
                if thread is not None:
                    INFINITE = 0xFFFFFFFF
                    ctypes.windll.kernel32.WaitForSingleObject(thread, INFINITE)
                    MEM_RELEASE = 0x8000
                    if ctypes.windll.kernel32.VirtualFreeEx(proc_handle, alloc_address, 0, MEM_RELEASE):
                        ret = True
    if proc_handle is not None:
        ctypes.windll.kernel32.CloseHandle(proc_handle)
    return ret

import psutil
def main():
    pids = psutil.pids()
    #第二步在快照中去比对进程名
    for pid in pids:
        p= psutil.Process(pid)
        if p.name()=="WeChat.exe":
            break
    print('pid:',pid)
    dllinject( r"F:\my_app\WeChatHelper\Debug\WeChatHelper.dll".encode("ascii"),pid)

    print("program completed.")

main()