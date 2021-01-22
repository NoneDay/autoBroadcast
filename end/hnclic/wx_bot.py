from datetime import datetime
import time
import os
from win32 import win32gui,win32api
import win32con, win32api, win32gui, ctypes, ctypes.wintypes
import chardet

class COPYDATASTRUCT(ctypes.Structure):
    _fields_ = [
        ('dwData', ctypes.wintypes.LPARAM),
        ('cbData', ctypes.wintypes.DWORD),
        ('lpData', ctypes.c_void_p)
    ]
PCOPYDATASTRUCT = ctypes.POINTER(COPYDATASTRUCT)

class Listener:

    def __init__(self):
        message_map = {
            win32con.WM_COPYDATA: self.OnCopyData
        }
        wc = win32gui.WNDCLASS()
        wc.lpfnWndProc = message_map
        wc.lpszClassName = 'MyWindowClass'
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        classAtom = win32gui.RegisterClass(wc)
        self.hwnd = win32gui.CreateWindow (classAtom,"微信助手",0,0, 0,
            win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,0, 0,hinst, None
        )
        print(self.hwnd)

    def OnCopyData(self, hwnd, msg, wparam, lparam):
        #print( hwnd)
        #print( msg)
        #print( wparam)
        #print( lparam)
        pCDS = ctypes.cast(lparam, PCOPYDATASTRUCT)
        #print( pCDS.contents.dwData)
        #print( pCDS.contents.cbData)
        string=ctypes.string_at(pCDS.contents.lpData).decode("gb2312")
        print( string)
        return 1


l = Listener()
#win32gui.PumpMessages()
import _thread
win32gui.PumpMessages()
#_thread.start_new_thread(win32gui.PumpMessages)
#
#import win32com.client
#WMI= win32com.client.GetObject('winmgmts:')
#processes = WMI.ExecQuery('SELECT * from win32_process')
#process_list = [i.Properties_('ProcessId').Value for i in processes if i.Properties_('Name').Value=="WeChat.exe"] # list of available processes
#import D2
#D2.inject_dll(r'f:\my_app\WeChatHelper\Debug\WeChatHelper.dll'.encode("ascii"), process_list[0])
#
#str = input("请输入：")