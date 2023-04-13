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
python src/client --scale   // specify the size of the chess window
python src/client --theme_id    // specify theme for game
```
Network :
- start the server
```
python src/server.py
```
- start the client
```
python src/client.py    // default ip address = 127.0.0.1
python src/client.py --server_ip    // specify server ip address
python src/client --scale   // specify the size of the chess window
python src/client --theme_id    // specify theme for game
```

# Resources
- sprites : https://dani-maccari.itch.io/pixel-chess
- fonts 
  - The Oleaguid font was made by Arynoc https://opengameart.org/content/oleaguid-font
  - The Quinquefive font\
  https://ggbot.itch.io/quinquefive-font
