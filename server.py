import socket
import _thread as thread


server = "192.168.1.44"
port = 5555
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind((server, port))
except socket.error as e:
	str(e)

s.listen(2)
print("Waiting for a connection, Server Started")


def threaded_client(conn):
	conn.send(str.encode("Connected"))
	reply = ""
	while True:
		try:
			data = conn.recv(2048)
			reply = data.decode("utf-8")

			if not data:
				print("Disconnected")
				break
			else:
				print("Received: ", reply)

			conn.sendall(str.encode('its me'))
		except:
			break

	print("Lost connection")
	conn.close()


while True:
	conn, addr = s.accept()
	print("Connected to:", addr)

	thread.start_new_thread(threaded_client, (conn,))
