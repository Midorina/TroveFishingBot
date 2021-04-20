import logging
from typing import Optional

from key_manager import Presser
from memory_models import Liquid
from process_memory_manager import Process


class Bot:
    def __init__(self):
        self.trove = Process.get_by_name("Trove.exe")

        self.liquids = Liquid.get_all(self.trove)

        self.throw_attempts = 0
        self.announced_thrown_liquid_type = False

    def get_liquid(self) -> Optional[Liquid]:
        for liquid in self.liquids:
            if liquid.pole_in_liquid or liquid.caught_fish:
                return liquid

    def bot_loop(self):
        # this method contains the main logic

        # scan all addresses and get the liquid
        liquid = self.get_liquid()

        # take action depending on scan result
        if not liquid:
            logging.info("Throwing the pole...")

            # inspect attempt counter
            if self.throw_attempts > 15:
                raise Exception(
                    "Too many attempts have been made to throw the pole but none of them were successful.")
            else:
                self.throw_attempts += 1

        # if we caught a fish
        elif liquid.caught_fish is True:
            logging.info(f"Caught a {liquid.name} type fish!")

            # reset counters
            self.throw_attempts = 0
            self.announced_thrown_liquid_type = False

        # if the pole is thrown, we just inform and wait
        else:
            if self.announced_thrown_liquid_type is False:
                logging.info(f"Thrown into {liquid}. Waiting to catch a fish...")
                self.announced_thrown_liquid_type = True
            Presser.not_precise_sleep(0.3, interval=0.1)
            return

        Presser.not_precise_sleep(0.1, interval=0.05)

        self.trove.focus()
        # TODO: find a way to send inputs without focusing (trove.send_input('f'))
        Presser.press_and_release(
            'f',
            # wait longer as more attempts are being made to avoid the bug
            # where your pole is thrown into the air
            sleep_between=0 + (self.throw_attempts * 0.015)
        )
        self.trove.focus_back_to_last_window()

        Presser.not_precise_sleep(1.6, interval=0.10)

    def start(self):
        script = Presser(self.bot_loop)
        script.start()
