import network as NET

n = NET.Network()

done = False

while not done:
	player_input = input('send to server :')
	response = n.send(player_input)
	print( response )
