import logging
import time
from typing import Optional

from managers.loop_manager import Manager
from internals.liquid import Liquid
from managers.process_memory_manager import Process


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

            self.announced_thrown_liquid_type = False
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

            time.sleep(0.2)
            return

        Manager.human_sleep(0.1, interval=0.02)

        self.trove.send_input('f', sleep_between=0.05)

        Manager.human_sleep(1.6, interval=0.07)

    def start(self):
        script = Manager(self.bot_loop)
        script.start()
