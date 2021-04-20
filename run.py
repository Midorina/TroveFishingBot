import logging
import subprocess
import time

from bot import Bot
from process_memory_manager import Process

logging.basicConfig(format='[%(asctime)s] %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)

while True:
    try:
        Bot().start()
    except Exception as e:
        logging.error(e)
        # if game/Steam crashes, or the character is stuck in throwing animation, or Trove isn't found
        logging.warning("Killing Trove and Steam...")
        Process.kill_by_name(['Trove.exe', 'GlyphClientApp.exe', 'GlyphCrashHandler64.exe',
                              'steam.exe', 'SteamService.exe', 'steamwebhelper.exe'])

        logging.warning("Re-launching...")
        # "Auto Launch Game On Start" needs to be enabled in order for this to work.
        subprocess.run("start steam://run/304050", shell=True)

        time.sleep(30.0)
    else:
        # if exited without errors, break the loop
        break
