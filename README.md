# Chess
Chess in pygame\
Requires python 3.10+

# Features
- Local : 
	- play on one computer, where two players take turns making the moves.
	- press "SPACE" to change the player perspective
- Network : play over the network
		  
# Instructions

Local :
- start local game
```
python src/local.py

Options:
    --scale
    --theme_id
    --pieces_asset
    --timer

```
Network :
- start the server
```
python src/server.py

Options:
    --timer
```
- start the client
```
python src/client.py

Options:
    --server_ip
    --scale
    --theme_id
    --pieces_asset


```
- Options description
```
-- timer  :  Choose timer settings.
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
  
--server_ip  :  specify server ip for client
    Default server ip = 127.0.0.1

--scale  :  specify size of application
    default size = 3.5
    not recommended to go below 2, font will become unreadable

--theme_id  :  Choose theme of the Game
    possible theme_id: 1, 2, 3, 4, -1
    -1 = Random theme
        

--pieces_asset  :  Choose Pieces Asset
    possible pieces Asset: SMALL, LARGE, RANDOM


```


# Resources
- sprites : https://dani-maccari.itch.io/pixel-chess
- fonts 
  - The Oleaguid font was made by Arynoc https://opengameart.org/content/oleaguid-font
  - The Quinquefive font\
  https://ggbot.itch.io/quinquefive-font
