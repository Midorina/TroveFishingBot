import ctypes
import functools
import logging
import time
from typing import List

import psutil
import win32api
import win32con
import win32gui
import win32process

from managers.loop_manager import Manager


class Process:
    def __init__(self, process_id: int, process_name: str, base_address):
        self.process_id = process_id
        self.process_name = process_name

        self.base_address = base_address

        self.__last_window_handle = None

    @functools.cached_property
    def process_handle(self):
        """We don't use the handle we got while getting the process by name,
        because that handle contains sub modules,
        which we don't want while reading the memory."""
        return ctypes.windll.kernel32.OpenProcess(win32con.PROCESS_VM_READ, False, self.process_id)

    @functools.cached_property
    def window_handle(self):
        """To focus, and send inputs"""
        title = self.process_name.split('.')[0].title()
        return win32gui.FindWindow(None, title)

    @classmethod
    def get_by_name(cls, process_name: str) -> "Process":
        """Finds a process by name and returns a Process object."""

        for process_id in win32process.EnumProcesses():
            # If process_id is the same as this program, skip it
            if process_id == -1:
                continue

            handle = None
            # Try to read the process memory
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                                              True, process_id)
            except:
                continue
            else:
                # iterate over an array of base addresses of each module
                for base_address in win32process.EnumProcessModules(handle):
                    # Get the name of the module
                    current_name = str(win32process.GetModuleFileNameEx(handle, base_address))

                    # compare it
                    if process_name.casefold() in current_name.casefold():
                        logging.debug(f"Base address of {process_name} ({process_id}): {hex(base_address)}")
                        return cls(process_id, process_name, base_address)

            finally:
                if handle:
                    # close the handle as we don't need it anymore
                    win32api.CloseHandle(handle)

        raise Exception(f"{process_name} could not be found.")

    def read_memory(self, address, offsets: List = None):
        """Reads memory using a base_address and a list of offsets (optional).
        Returns a pointer and a value."""

        # Pointer to the data want to read
        data = ctypes.c_uint(0)

        # Size of the variable, 4 bytes
        bytes_read = ctypes.c_uint(0)

        # Starting address
        current_address = address

        if offsets:
            for offset in offsets:
                # Convert to int if its str
                if isinstance(offset, str):
                    offset = int(offset, 16)

                # Read the memory of current address using ReadProcessMemory
                ctypes.windll.kernel32.ReadProcessMemory(self.process_handle, current_address, ctypes.byref(data),
                                                         ctypes.sizeof(data), ctypes.byref(bytes_read))

                # Replace the address with the new data address
                current_address = data.value + offset
        else:
            # Just read the single memory address
            ctypes.windll.kernel32.ReadProcessMemory(self.process_handle, current_address, ctypes.byref(data),
                                                     ctypes.sizeof(data),
                                                     ctypes.byref(bytes_read))

        # Return a pointer to the value and the value
        # If current offset is `None`, return the value of the last offset
        logging.debug(f"(Address: {hex(current_address)}) Value: {data.value}")
        return current_address, data.value

    def focus(self):
        """Focuses on the process window."""
        self.__last_window_handle = win32gui.GetForegroundWindow()

        if self.__last_window_handle != self.window_handle:
            exc = None

            # try 2 times
            for _ in range(2):
                try:
                    # for some reason this doesn't work without sending an alt key first
                    Manager.press_and_release('alt', sleep_between=0)
                    win32gui.SetForegroundWindow(self.window_handle)

                except Exception as e:
                    # del the attribute to update it
                    delattr(self, 'window_handle')

                    exc = e
                    time.sleep(0.1)
                else:
                    return

            raise exc

    def focus_back_to_last_window(self):
        """Focuses back to the last window that was active before focusing on our process."""
        if self.__last_window_handle != self.window_handle:

            # SetForegroundWindow doesn't work without sending 'alt' first
            Manager.press_and_release('alt', sleep_between=0)

            try:
                win32gui.SetForegroundWindow(self.__last_window_handle)
            except:
                # if we couldn't focus back, its fine, just ignore
                pass

    @staticmethod
    def kill_by_name(names: List[str]):
        """Kill every process by specified list of names."""
        names = list(map(lambda x: x.casefold(), names))

        for proc in psutil.process_iter():
            if proc.name().casefold() in names:
                try:
                    proc.kill()
                except psutil.AccessDenied:
                    logging.debug(f'Could not kill process "{proc.name()}". Ignoring.')
                except psutil.NoSuchProcess:
                    pass

    @staticmethod
    def char2key(c):
        """Converts a key to a Windows Virtual Key code."""

        # https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-vkkeyscanw
        result = ctypes.windll.User32.VkKeyScanW(ord(c))

        # shift_state = (result & 0xFF00) >> 8
        vk_key = result & 0xFF

        return vk_key

    def send_input(self, key: str, sleep_between: float = 0):
        """Sends a key input straight to the process. This took me a lot of time, but it was worth it."""

        # get the virtual key code
        vk = self.char2key(key)

        # compute the lParam
        l_param = win32api.MapVirtualKey(vk, 0) << 16

        # send the input
        win32api.PostMessage(self.window_handle, win32con.WM_KEYDOWN, vk, l_param | 0x00000001)
        time.sleep(sleep_between)
        win32api.PostMessage(self.window_handle, win32con.WM_KEYUP, vk, l_param | 0x20000001)

    def __del__(self):
        """Close the handle when our object gets garbage collected."""
        if self.process_handle:
            ctypes.windll.kernel32.CloseHandle(self.process_handle)
