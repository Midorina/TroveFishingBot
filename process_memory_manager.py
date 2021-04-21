import ctypes
import logging
import time
from typing import List

import psutil
import win32api
import win32con
import win32gui
import win32process

import key_manager


class Process:
    def __init__(self, process_id: int, process_name: str, process_handle, base_address):
        self.process_id = process_id
        self.process_name = process_name

        self.base_address = base_address

        self._process_handle = process_handle
        self._window_handle = None
        self.__last_window_handle = None

    def __del__(self):
        win32api.CloseHandle(self._process_handle)

    @classmethod
    def get_by_name(cls, process_name: str) -> "Process":
        """Finds the process id of the given
        process name and returns the process id and its base address."""

        for process_id in win32process.EnumProcesses():
            # If process_id is the same as this program, skip it
            if process_id == -1:
                continue

            # Try to read the process memory
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ,
                                              True, process_id)
            except:
                continue

            # iterate over an array of base addresses of each module
            for base_address in win32process.EnumProcessModules(handle):
                # Get the name of the module
                current_name = str(win32process.GetModuleFileNameEx(handle, base_address))

                # Compare it to the name of your program
                if process_name.casefold() in current_name.casefold():
                    logging.debug(f"Base address of {process_name} ({process_id}): {hex(base_address)}")
                    return cls(process_id, process_name, handle, base_address)

        raise Exception(f"{process_name} could not be found.")

    def read_memory(self, address, offsets: List = None):
        """Read a process' memory based on its process id, address and offsets.
        Returns the address without offsets and the value."""

        logging.debug(f"Address of the memory that's going to be read: {hex(address)}")

        # The handle to the program's process
        # This will allow to use ReadProcessMemory
        h_process = ctypes.windll.kernel32.OpenProcess(win32con.PROCESS_VM_READ, False, self.process_id)

        # This is a pointer to the data you want to read
        # Use `data.value` to get the value at this pointer
        # In this case, this value is an Integer with 4 bytes
        data = ctypes.c_uint(0)

        # Size of the variable, it usually is 4 bytes
        bytes_read = ctypes.c_uint(0)

        # Starting address
        current_address = address

        if offsets:
            # Append a new element to the offsets array
            # This will allow you to get the value at the last offset
            offsets.append(None)

            for offset in offsets:
                # Convert to int if its str
                if isinstance(offset, str):
                    offset = int(offset, 16)

                # Read the memory of current address using ReadProcessMemory
                ctypes.windll.kernel32.ReadProcessMemory(h_process, current_address, ctypes.byref(data),
                                                         ctypes.sizeof(data), ctypes.byref(bytes_read))

                # If current offset is `None`, return the value of the last offset
                if not offset:
                    logging.debug(f"(Address: {hex(current_address)}) Value: {data.value}")
                    return current_address, data.value
                else:
                    # Replace the address with the new data address
                    current_address = data.value + offset

        else:
            # Just read the single memory address
            ctypes.windll.kernel32.ReadProcessMemory(h_process, current_address, ctypes.byref(data),
                                                     ctypes.sizeof(data),
                                                     ctypes.byref(bytes_read))

        # Close the handle to the process
        # ctypes.windll.kernel32.CloseHandle(h_process)

        # Return a pointer to the value and the value
        # The pointer will be used to write to the memory
        return current_address, data.value

    # def _window_enum_handler(self, window_handle, process_name):
    #     if win32gui.GetWindowText(window_handle).casefold() == process_name:
    #         self._window_handle = window_handle

    @property
    def window_handle(self):
        if self._window_handle is None:
            title = self.process_name.split('.')[0].title()
            self._window_handle = win32gui.FindWindow(None, title)

        return self._window_handle

    def focus(self):
        self.__last_window_handle = win32gui.GetForegroundWindow()

        if self.__last_window_handle != self.window_handle:
            # send an alt key first to make this work
            key_manager.Presser.press_and_release('alt', sleep_between=0)

            exc = None
            # try 2 times
            for _ in range(2):
                try:
                    win32gui.SetForegroundWindow(self.window_handle)
                except Exception as e:
                    exc = e
                    time.sleep(0.1)
                else:
                    return

            raise exc

    def focus_back_to_last_window(self):
        if self.__last_window_handle != self.window_handle:
            key_manager.Presser.press_and_release('alt', sleep_between=0)
            win32gui.SetForegroundWindow(self.__last_window_handle)

    @staticmethod
    def kill_by_name(names: List[str]):
        for proc in psutil.process_iter():
            if proc.name() in names:
                try:
                    proc.kill()
                except psutil.AccessDenied:
                    logging.debug(f'Could not kill process "{proc.name()}". Ignoring.')

    # @staticmethod
    # def char2key(c):
    #     # https://msdn.microsoft.com/en-us/library/windows/desktop/ms646329(v=vs.85).aspx
    #     result = ctypes.windll.User32.VkKeyScanW(ord(unicode(c)))
    #     shift_state = (result & 0xFF00) >> 8
    #     vk_key = result & 0xFF
    #
    #     return vk_key
    #
    # def send_input(self, key: str):
    #     win32api.SendMessage(self.window_handle, win32con.WM_CHAR, ord(key), 0)
    #
    #     ret1 = win32api.PostMessage(self.window_handle, win32con.WM_KEYDOWN, ord(key), 0)
    #     ret2 = win32api.PostMessage(self.window_handle, win32con.WM_KEYUP, ord(key), 0)
    #
    #     print("ret1 and ret2:", ret1, ret2)
