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
- python src/local.py
```
Network :
- start the server
```
python src/server.py	// default ip address = 127.0.0.1
python src/server.py --ip	// specified ip adress
```
- start the client
```
python src/client.py		// default ip address = 127.0.0.1
python src/client.py --server_ip	// specified server ip address
```

# Resources
- sprites : https://dani-maccari.itch.io/pixel-chess
- font : https://opengameart.org/content/oleaguid-font
  - The Oleaguid font was made by Arynoc
