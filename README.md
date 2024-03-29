# Chess
Chess in pygame\
Requires:
  - python 3.11.4

Optional:  
  - Stockfish 15.1 https://stockfishchess.org/download/

# Features
 - Play against other Player on same machine
 - Play against other Player on the local network
 - Start server on the local network
 - Play against stock fish bot
 - Watch stock fish play against itself
 - tkinter launcher
		  
# Instructions
```
# use stockfish
download the stockfish engine - https://stockfishchess.org/download/
copy the path of the engine and paste it into the
bot path entry inside the launcher

# start launcher
python src/main.py

#start server
python src/main.py --app_type "SERVER"

#start player vs player on same machine
python src/main.py --app_type "PLAYER_V_PLAYER"
    options:
        --scale
        --theme_id
        --pieces_asset
        --timer
```

# Options description
```
--app_type : select what to launch. 
    LAUNCHER, SERVER, PLAYER_V_PLAYER
    default = LAUNCHER

--timer  :  Choose timer settings.
    Custom setting format: 
        "time increment" 
        (time-minutes, increment-seconds)
        e.g "15 0"
    possible timers:
        BULLET_1_0 
        BULLET_1_1 
        BULLET_2_1
        BLITZ_3_0 
        BLITZ_3_2 
        BLITZ_5_0
        RAPID_15_10 
        RAPID_30_0 
        RAPID_60_0
  
--scale  :  specify size of application
    default size = 3.5
    not recommended to go below 2, font will become unreadable

--theme_id  :  Choose theme of the Game
    possible theme_id: 1, 2, 3, 4, -1
    -1 = Random theme
        
--pieces_asset  :  Choose Pieces Asset
    possible pieces Asset: SMALL, LARGE, RANDOM

```

# Flags description

```
--server_log_stdout : sets server log output to stdout

--client_log_stdout : sets client log output to stdout

--bot_log_stdout : sets chess bot log output to stdout

--database_log_stdout : sets database log output to stdout

--launcher_log_stdout : sets launcher log output to stdout
```

# Problems
 - if windows is timing out incoming connections to the local server,
you must allow python through the Windows Firewall.
https://stackoverflow.com/questions/53231849/python-socket-windows-10-connection-times-out

# Resources
- sprites : https://dani-maccari.itch.io/pixel-chess
- fonts 
  - The Oleaguid font was made by Arynoc https://opengameart.org/content/oleaguid-font
  - The Quinquefive font\
  https://ggbot.itch.io/quinquefive-font
