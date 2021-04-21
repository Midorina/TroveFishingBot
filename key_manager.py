# midorina.dev
import logging
import random
import time
from threading import Thread

import keyboard


class Presser:
    def __init__(self, func: callable, quit_key: str = 'ctrl+q', pause_key: str = 'ctrl+p'):
        self.main_loop_thread = None
        self.main_loop_thread_exc = None

        self.paused = False
        self._exit = False

        self.func = func

        self.quit_key = quit_key
        self.pause_key = pause_key

        keyboard.add_hotkey(quit_key, lambda: self.exit())
        keyboard.add_hotkey(pause_key, lambda: self.pause_or_resume())

    def pause_or_resume(self):
        if self.paused is False:
            logging.info("Pausing...")
        else:
            logging.info("Resuming...")
        self.paused = not self.paused

    def exit(self):
        logging.info("Exiting...")
        self._exit = True

    def main_loop(self):
        while True:
            if self._exit is True:
                return

            if self.paused is True:
                keyboard.wait(self.pause_key)

            try:
                self.func()
            except Exception as e:
                self.main_loop_thread_exc = e
                return

    def start(self):
        logging.info(f'Starting in 5 seconds. Press "{self.pause_key}" to pause/resume and "{self.quit_key}" to exit.')
        time.sleep(5.0)

        self.main_loop_thread = Thread(target=self.main_loop)
        self.main_loop_thread.start()
        self.main_loop_thread.join()

        # raise if there was an exception
        if self.main_loop_thread_exc:
            raise self.main_loop_thread_exc

    @staticmethod
    def press_and_release(button: str,
                          sleep_before: float = 0,
                          sleep_between: float = 0,
                          sleep_after: float = 0,
                          precise: bool = False):
        if precise is True:
            sleep = time.sleep
        else:
            sleep = Presser.human_sleep

        sleep(sleep_before)
        keyboard.press(button)
        sleep(sleep_between)
        keyboard.release(button)
        sleep(sleep_after)

    @staticmethod
    def human_sleep(length: float, interval: float = None):
        # 10% inconsistency
        interval = interval or length / 10
        time.sleep(random.uniform(length - interval, length + interval))
