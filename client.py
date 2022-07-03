import sys
import select
import socket

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('10.0.2.15', 8888))
    sock.setblocking(False)

    def obtain_data(client_socket):
        try:
            msg_len = client_socket.recv(5)

            if not len(msg_len):
                return False

            message_length = int(msg_len.decode('utf-8').strip())
            return {'Length': msg_len, 'data': client_socket.recv(message_length)}

        except:
            return False

    name = (input("Enter Name: "))
    sock.send(name.encode('utf-8'))

    while True:
    	sockets_list = [sys.stdin, sock]
    	readList, writeList, error_soc = select.select(sockets_list,[],[])
    	for socket in readList:
    		if socket == sock:
    			encoded_message = obtain_data(socket)
    			if not encoded_message :
    				print("Session has ended")
    				sys.exit()
    			else:
    				message = encoded_message['data'].decode('utf-8')
    				print(message)

    		else:
    			message = sys.stdin.readline()
    			sock.send(message.encode('utf-8'))
    sock.close()
    sys.exit()
