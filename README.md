# Chess
Chess in pygame


# Resources
- sprites : https://dani-maccari.itch.io/pixel-chess

# Features
- Local : play on one computer, where two players take turns making the moves.
- Network : play over the network
		  
# Instructions

Local :
- python local.py -> start local game

Network :
To play over the network you must start the server before the clients can join.
the default ip adress of the server is 127.0.0.1 for both the client and the server script
- python server.py -> start the server\
	'--ip' option to specify the ip adress for the server
- python client.py -> start the client\
	'--server_ip' option to specify the ip adress the client will connect to



# Limitations:
- if more that 2 players connect, the third player will share the board with one of the other players
- in order for the game to be properly synced up, the first client to connect must wait for the other client to join in order to make the first move. if you dont wait the move suggestion highlighting will NOT work
