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
        self.last_throw_datetime = None  # keep track of the last throw datetime to prevent fake caught fish signals
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
            self.last_throw_datetime = time.time()
            self.announced_thrown_liquid_type = False

            # inspect attempt counter
            if self.throw_attempts > 15:
                raise Exception(
                    "Too many attempts have been made to throw the pole but none of them were successful.")
            else:
                self.throw_attempts += 1

        # if we caught a fish
        elif liquid.caught_fish is True:
            # trove implemented anti fish bot measures where they manipulate the "caught water type fish" pointer
            # to 1 at the beginning of a throw. so, we need to wait a bit to make sure we caught a fish
            if self.last_throw_datetime is not None and time.time() - self.last_throw_datetime < 5.5:
                logging.debug(f"Received fake caught fish signal after {time.time() - self.last_throw_datetime:.2f} "
                              f"seconds. Ignoring...")
                time.sleep(0.2)
                return

            logging.info(f"Caught a {liquid.name} type fish!")

            # reset counters
            self.throw_attempts = 0
            self.last_throw_datetime = None
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
