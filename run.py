import logging
import subprocess
import time

from internals.bot import Bot
from managers.process_memory_manager import Process

logging.basicConfig(format='[%(asctime)s.%(msecs)03d] %(message)s', datefmt='%d-%m-%Y %H:%M:%S', level=logging.INFO)

while True:
    try:
        Bot().start()
    except Exception as e:
        logging.debug("Ignoring exception:", exc_info=True)

        # if game/Steam crashes, or the character is stuck in throwing animation, or Trove isn't found
        logging.error(str(e))
        logging.warning("Killing Trove and Steam in 5 seconds...")
        time.sleep(5.0)

        Process.kill_by_name(['Trove.exe', 'GlyphClientApp.exe', 'GlyphCrashHandler64.exe',
                              'steam.exe', 'SteamService.exe', 'steamwebhelper.exe'])

        logging.warning("Re-launching...")
        # "Auto Launch Game On Start" needs to be enabled in order for this to work.
        subprocess.run("start steam://run/304050", shell=True)

        time.sleep(60.0)
    else:
        # if exited without errors, break the loop
        break
