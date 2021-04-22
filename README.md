# TroveFishingBot
An advanced Trove Fishing bot that works in the background, written in Python.

## Features
- It supports fishing in every kind of liquid (Water, Plasma, Lava, Chocolate)
- It sends the input using Windows API, which means it can work in the background without interrupting you at all.
- It uses random sleep times to behave like a human.
- Trove crashes a lot (it sometimes crashes Steam as well), and in case of a crash (or stuck animation), it restarts the game.
- It reads the game's memory instead of processing image/sound, thus low CPU usage.

## How to Download/Use
**If this is not your first time running this bot, you only need to do Steps 2 and 5.** 
1) Change your Glyph Launcher settings like this to allow the bot to easily restart the game when needed.
![Glyph Launcher Settings](https://i.imgur.com/DDtltll.png)

2) Start the game and position yourself in a place where you can throw the pole easily without having to aim precisely (towards any liquid).
![Example position](https://i.imgur.com/Tkp3cvT.png)

3) Open a command prompt and download the bot by cloning this repo:
```
git clone https://github.com/Midorina/TroveFishingBot
```
4) CD into the folder
```
cd TroveFishingBot
```
5) Download the required modules
```
python -m pip install -r requirements.txt
```
6) Start the script by running ``run.py``
```
python run.py
```

There you go! The bot will start in a few seconds and start fishing for you.
- Press CTRL+P to pause/resume
- Press CTRL+Q to quit

## Suggestions
- Clean up your inventory before starting the bot to avoid filling up your inventory quickly.
- Don't fish in public and crowded places (such as hub)
- Enable "Settings -> Social -> Appear Offline" in-game to prevent other people from joining you.
- Disable "Settings -> Audio -> Play audio when in the background" in-game so that fish sounds don't annoy you.
- You can start the bot before launching the game. Bot will open the game for you. Though, if your character isn't positioned properly, this will not work.

## TODO
- Support multiple instances
- Automatically trash ancient boots
- Automatically loot-collect

## Known Issues
- If you use a laptop and close the lid, the game kind of stops responding or we are not able to read the memory properly anymore, so don't do that.
- Sometimes, If the bot is paused for too long with CTRL+P, the window handle becomes invalid for some reason, so I suggest restarting the bot in such cases.