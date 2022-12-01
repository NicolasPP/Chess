# Chess
Chess in pygame


# Resources
- sprites : https://dani-maccari.itch.io/pixel-chess
		  
# Running
- you can play single player, where you on one computer and press space to change players perspective

- you can also play over the network. MUST be on the same network. Furthermore you must change the ip address in network.py in order for multiplayer to work.
	
	- first you must run server.py
	- at this point the clients can start joining
	- to join run client.py

	- Limitations:
		- if more that 2 players connect, the third player will share the board with one of the other players
		- in order for the game to be properly synced up, the first client to connect must wait for the other client to join in order to make the first move. if you dont wait the move suggestion highlighting will NOT work
