#PID = int(input('Enter the PID of the process '))
import ctypes
import sys

def inject_dll(dllpath, pid):
    shellcode = bytearray(b"\x56"                                                 # PUSH ESI
                          b"\x57"                                                 # PUSH EDI
                          b"\xFC"                                                 # CLD
                          b"\x6A\x30"                                             # PUSH 30h
                          b"\x5E"                                                 # POP ESI
                          b"\x64\xAD"                                             # LODS DWORD PTR FS:[ESI]
                          b"\x89\xC2"                                             # MOV EDX, EAX
                          b"\x8B\x52\x0C"                                         # MOV EDX, DWORD PTR DS:[EDX+0Ch]
                          b"\x8B\x52\x14"                                         # MOV EDX, DWORD PTR DS:[EDX+14h]
                                                                                  # NEXT_MODULE:
                          b"\x8B\x72\x28"                                         # MOV ESI, DWORD PTR DS:[EDX+28h]
                          b"\xB9\x18\x00\x00\x00"                                 # MOV ECX, 18h
                          b"\x31\xFF"                                             # XOR EDI, EDI
                                                                                  # NEXT_CHAR:
                          b"\x31\xC0"                                             # XOR EAX, EAX
                          b"\xAC"                                                 # LODSB
                          b"\x3C\x61"                                             # CMP AL, 'a'
                          b"\x7C\x02"                                             # JL SHORT ALREADY_UPPER_CASE
                          b"\x2C\x20"                                             # SUB AL, 20h
                                                                                  # ALREADY_UPPER:
                          b"\xC1\xCF\x0D"                                         # ROR EDI, 0Dh
                          b"\x01\xC7"                                             # ADD EDI, EAX
                          b"\xE2\xF0"                                             # LOOP NEXT_CHAR
                          b"\x81\xFF\x5B\xBC\x4A\x6A"                             # CMP EDI, 6A4ABC5Bh
                          b"\x8B\x42\x10"                                         # MOV EAX, DWORD PTR DS:[EDX+10h]
                          b"\x8B\x12"                                             # MOV EDX, DWORD PTR DS:[EDX]
                          b"\x75\xD9"                                             # JNZ SHORT NEXT_MODULE
                          b"\x5F"                                                 # POP EDI
                          b"\x5E"                                                 # POP ESI
                          b"\x89\xC2"                                             # MOV EDX, EAX
                          b"\xE8\x00\x00\x00\x00"                                 # CALL DELTA
                                                                                  # DELTA:
                          b"\x5D"                                                 # POP EBP
                          b"\x89\xD3"                                             # MOV EBX, EDX
                          b"\x8B\x53\x3C"                                         # MOV EDX, DWORD PTR DS:[EBX+3Ch]
                          b"\x01\xDA"                                             # ADD EDX, EBX
                          b"\x8B\x52\x78"                                         # MOV EDX, DWORD PTR DS:[EDX+78h]
                          b"\x01\xDA"                                             # ADD EDX, EBX
                          b"\x8B\x72\x20"                                         # MOV ESI, DWORD PTR DS:[EDX+20h]
                          b"\x01\xDE"                                             # ADD ESI, EBX
                          b"\x31\xC9"                                             # XOR ECX, ECX
                                                                                  # FIND_GET_PROC_ADDR:
                          b"\x41"                                                 # INC ECX
                          b"\xAD"                                                 # LODSD
                          b"\x01\xD8"                                             # ADD EAX, EBX
                          b"\x81\x38\x47\x65\x74\x50"                             # CMP DWORD PTR DS:[EAX], "GetP"
                          b"\x75\xF4"                                             # JNZ FIND_GET_PROC_ADDR
                          b"\x81\x78\x04\x72\x6F\x63\x41"                         # CMP DWORD PTR DS:[EAX+4], "rocA"
                          b"\x75\xEB"                                             # JNZ FIND_GET_PROC_ADDR
                          b"\x81\x78\x08\x64\x64\x72\x65"                         # CMP DWORD PTR DS:[EAX+8], "ddre"
                          b"\x75\xE2"                                             # JNZ FIND_GET_PROC_ADDR
                          b"\x66\x81\x78\x0C\x73\x73"                             # CMP WORD PTR DS:[EAX+C], "ss"
                          b"\x75\xDA"                                             # JNZ FIND_GET_PROC_ADDR
                          b"\x8B\x72\x24"                                         # MOV ESI, DWORD PTR DS:[EDX+24h]
                          b"\x01\xDE"                                             # ADD ESI, EBX
                          b"\x0F\xB7\x0C\x4E"                                     # MOVZX ECX, WORD PTR DS:[ESI+ECX*2]
                          b"\x49"                                                 # DEC ECX
                          b"\x8B\x72\x1C"                                         # MOV ESI, DWORD PTR DS:[EDX+1Ch]
                          b"\x01\xDE"                                             # ADD ESI, EBX
                          b"\x8B\x14\x8E"                                         # MOV EDX, DWORD PTR DS:[ESI+ECX*4]
                          b"\x01\xDA"                                             # ADD EDX, EBX
                          b"\x89\x95\x8D\x00\x00\x00"                             # MOV DWORD PTR SS:[EBP+8Dh], EDX
                          b"\x8D\x75\x7C"                                         # LEA ESI, DWORD PTR SS:[EBP+7Ch]
                          b"\x8D\xBD\x89\x00\x00\x00"                             # LEA EDI, DWORD PTR SS:[EBP+89h]
                          b"\x56"                                                 # PUSH ESI
                          b"\x57"                                                 # PUSH EDI
                          b"\x51"                                                 # PUSH ECX
                          b"\x53"                                                 # PUSH EBX
                          b"\x56"                                                 # PUSH ESI
                          b"\x53"                                                 # PUSH EBX
                          b"\xFF\x95\x8D\x00\x00\x00"                             # CALL DWORD PTR SS:[EBP+8Dh]
                          b"\x5B"                                                 # POP EBX
                          b"\x59"                                                 # POP ECX
                          b"\x5F"                                                 # POP EDI
                          b"\x5E"                                                 # POP ESI
                          b"\xAB"                                                 # STOSD
                          b"\x8D\x85\x91\x00\x00\x00"                             # LEA, DWORD PTR SS:[EBP+91h]
                          b"\x50"                                                 # PUSH EAX
                          b"\xFF\x95\x89\x00\x00\x00"                             # CALL DWORD PTR SS:[EBP+89h]
                          b"\xC3"                                                 # RET
                          b"\x4C\x6F\x61\x64\x4C\x69\x62\x72\x61\x72\x79\x41\x00" # DB "LoadLibraryA", 0
                          b"\x00\x00\x00\x00"                                     # DD 0
                          b"\x00\x00\x00\x00")                                    # DD 0
    ret = False
    PROCESS_ALL_ACCESS =  (0x000F0000|0x00100000|0xFFF)
    proc_handle = ctypes.windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, None, pid)
    if proc_handle is not None:
        MEM_COMMIT = 0x00001000
        MEM_RESERVE = 0x00002000
        PAGE_EXECUTE_READWRITE = 0x40
        temp_buffer = shellcode + ctypes.create_string_buffer(dllpath).raw
        alloc_address = ctypes.windll.kernel32.VirtualAllocEx(proc_handle, None,
                                                              len(temp_buffer), MEM_RESERVE|MEM_COMMIT,
                                                              PAGE_EXECUTE_READWRITE)
        if alloc_address is not None:
            c_buffer = (ctypes.c_char * len(temp_buffer)).from_buffer(temp_buffer)
            if ctypes.windll.kernel32.WriteProcessMemory(proc_handle, alloc_address, c_buffer, len(temp_buffer), None):
                thread = ctypes.windll.kernel32.CreateRemoteThread(proc_handle, None, 0, alloc_address, None, 0, None)
                if thread is not None:
                    INFINITE = 0xFFFFFFFF
                    ctypes.windll.kernel32.WaitForSingleObject(thread, INFINITE)
                    MEM_RELEASE = 0x8000
                    if ctypes.windll.kernel32.VirtualFreeEx(proc_handle, alloc_address, 0, MEM_RELEASE):
                        ret = True
    if proc_handle is not None:
        ctypes.windll.kernel32.CloseHandle(proc_handle)
    return ret

def on_message(ws, message):
    # print(ws)
    print(message)


def on_error(ws, error):
    # print(ws)
    print(error)


def on_close(ws):
    # print(ws)
    print("### closed ###")
    print("reconnect")
    
def start_websock(ws):
    ws.run_forever()


import win32com.client
import win32gui
import websocket,time, threading

if __name__ == "__main__":
    WMI= win32com.client.GetObject('winmgmts:')
    processes = WMI.ExecQuery('SELECT * from win32_process')
    process_list = [i.Properties_('ProcessId').Value for i in processes if i.Properties_('Name').Value=="WeChat.exe"] # list of available processes
    
    #ws = websocket.create_connection("ws://127.0.0.1:10001")
    #ws.send(str({"op":"汉字"}))
    #print("Receiving...")
    #result =  ws.recv()
    #print(str(result))

    #inject_dll(r'f:\my_app\WeChatHelper\Debug\WeChatHelper.dll'.encode("ascii"), process_list[0])
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:10001",
                                on_message=on_message,
                                on_error=on_error,
                                on_close=on_close)
    t = threading.Thread(target=start_websock, name='LoopThread',args=(ws,))
    t.start()
    t.join()
