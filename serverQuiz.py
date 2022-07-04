import sys
import select
import socket
import time
import random
from question import question_and_answer
from _thread import *

class Communicate:
    def deliver_player(self, receiver, message):
    	message = f"{len(message):<5}" + message
    	try:
    		receiver.send(message.encode('utf-8'))
    	except:
    		receiver.close()
    		list_of_clients.remove(receiver)

    def broadcast_all(self, sender, message):
    	message = f"{len(message):<5}" + message
    	for socket in list_of_clients:
    		if (socket != sock and socket != sender):
    			try:
    				socket.send(message.encode('utf-8'))
    			except:
    				socket.close()
    				list_of_clients.remove(socket)

class Quiz:
    def transmit_question(self):
    	if len(question_and_answer) != 0:
    		q_n_a = question_and_answer[0]
    		question = q_n_a[0]
    		options = q_n_a[1]
    		Answer = q_n_a[2]

    		random.shuffle(options)
    		option_number = 1

    		a.broadcast_all(sock, "\nQ. " + str(question))
    		print("\nQ. " + str(question))
    		for j in range(len(options)):
    			a.broadcast_all(sock, "   " + str(option_number) + ") " + str(options[j]))
    			print("   " + str(option_number) + ") " + str(options[j]))
    			if options[j] == Answer:
    				answer.pop(0)
    				answer.append(int(option_number))
    			option_number += 1
    		a.broadcast_all(sock, "\nPress Enter on your keyboard to answer")
    		print("Answer: option number " + str(answer))
    	else:
    		a.broadcast_all(sock, "All questions already asked!")
    		self.quit_quiz()
    		sys.exit()

    def quiz(self):
    		Person[0] = sock
    		random.shuffle(question_and_answer)
    		b.transmit_question()
    		keypress = select.select(list_of_clients, [], [], 10)
    		if len(keypress[0]) > 0:
    			who_buzzed = keypress[0][0]
    			a.deliver_player(who_buzzed, "You pressed the buzzer first")
    			a.deliver_player(who_buzzed, "Input your answer(option 1, 2, 3 or 4): ")
    			a.broadcast_all(who_buzzed, "Someone already pressed the buzzer, you are too slow")
    			print("Buzzer was pressed")
    			time.sleep(0.01)
    			Person.pop(0)
    			Person.append(who_buzzed)
    			t0 = time.time()
    			question_and_answer.pop(0)

    			answering = select.select(Person, [], [], 10)
    			if len(answering) > 0:
    				if time.time() - t0 >= 5:
    					a.deliver_player(who_buzzed, "Too late to answer!")
    					a.broadcast_all(sock, str(players[mapping[who_buzzed]]) + " -0.5")
    					print(str(players[mapping[who_buzzed]]) + " -0.5")
    					self.renew_score(who_buzzed, -0.5)
    					time.sleep(3)
    					self.quiz()
    				else:
    					time.sleep(3)
    					self.quiz()
    			else:
    				print("None!")
    		else:
    			a.broadcast_all(sock, "No one has pressed the buzzer!")
    			print("Buzzer was not pressed by any player")
    			time.sleep(3)
    			question_and_answer.pop(0)
    			self.quiz()

    def renew_score(self, player, number):
    	print(players[mapping[player]])
    	marks[players[mapping[player]]] += number
    	print(marks)
    	a.broadcast_all(sock, "\nScore: ")
    	for j in marks:
    		a.broadcast_all(sock, ">> " + str(j) + ": " + str(marks[j]))

    def quit_quiz(self):
    	a.broadcast_all(sock, "End of Quiz\n")
    	print("End of Quiz\n")
    	for i in marks:
    		if marks[i] >= 5:
    			a.broadcast_all(sock, "The winner is: " + str(i))
    	a.broadcast_all(sock, "Scoreboard:")
    	print("Scoreboard: ")
    	for i in marks:
    		a.broadcast_all(sock, ">> " + str(i) + ": " + str(marks[i]))
    		print(">> " + str(i) + ": " + str(marks[i]))
    	sys.exit()

if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    player_num = int(input("Please enter the number of players(max allowed is 4): "))
    player_joined = 0

    if player_num > 4 or player_num < 1:
    	while player_num > 4 or player_num < 1:
    		player_num = int(input("Invalid number. Please input valid number: "))

    sock.bind(('', 8888))
    sock.listen(8)

    print("Waiting for connection from clients...")

    list_of_clients = []
    players = {}
    marks = {}
    mapping = {}
    Person = [sock]
    answer = [-1]

    a = Communicate()
    random.shuffle(question_and_answer)
    b = Quiz()

    list_of_clients.append(sock)

    while True:
    	readList, writeList, error_soc = select.select(list_of_clients, [], [])
    	for socket in readList:
    		if socket == sock:
    			client_socket, client_address = sock.accept()
    			if player_joined == player_num:
    				a.deliver_player(client_socket, "All players have joined!")
    				client_socket.close()
    			else:
    				name = client_socket.recv(1024).decode('utf-8')
    				if name:
    					if name in players.values():
    						a.deliver_player(client_socket, "Pick another name! Someone has picked this name")
    						client_socket.close()
    					else:
    						players[client_address] = name
    						marks[name] = 0
    						player_joined += 1
    						mapping[client_socket] = client_address
    						list_of_clients.append(client_socket)
    						print("Player has connected: " + str(client_address) +" [ " + players[client_address] + " ]" )
    						if player_joined < player_num:
    							a.deliver_player(client_socket, "Welcome to the quiz " + name + "!\nWait for others to join in...")

    						if player_joined == player_num:
    							a.broadcast_all(sock, "\nAll players have entered:")
    							for i in players:
    								a.broadcast_all(sock,">> " + players[i])
    							a.broadcast_all(sock, "\nThe quiz is starting in 10 seconds. Read the guide thoroughly.\n")
    							guide = """Guide:
        > You are provided 10 seconds to answer each question given.
        > Press enter to answer a question. The fastest player to press will get to answer.
        > You are given 5 seconds to answer the question.

        > Answer correctly to receive 1 point.
        > Answering wrong will cause you to lose 0.5 point.
        > Any player that manage to gain 5 points first win the quiz game."""
    							a.broadcast_all(sock, guide)
    							print("\n" + str(player_num) + " players have joined! Be prepared as the quiz will start in 10 seconds")
    							time.sleep(10)
    							start_new_thread(b.quiz, ())
    		else:
    			msg = socket.recv(1024).decode('utf-8')
    			print(msg)
    			if socket == Person[0]:
    				try:
    					ans = int(msg)
    					if ans == answer[0]:
    						a.deliver_player(socket, "Your answer is CORRECT")
    						a.broadcast_all(sock, str(players[mapping[socket]]) + " +1")
    						print(str(players[mapping[socket]]) + " +1")
    						b.renew_score(socket, 1)
    						Person[0] = sock
    						if marks[players[mapping[socket]]] >= 5:
    							b.quit_quiz()

    					else:
    						a.deliver_player(socket, "Your answer is WRONG")
    						a.broadcast_all(sock, str(players[mapping[socket]]) + " -0.5")
    						print(str(players[mapping[socket]]) + " -0.5")
    						b.renew_score(socket, -0.5)
    						Person[0] = sock
    				except ValueError:
    					a.deliver_player(socket, "INVALID Answer")
    					a.broadcast_all(sock, str(players[mapping[socket]]) + " -0.5")
    					print(str(players[mapping[socket]]) + " -0.5")
    					b.renew_score(socket, -0.5)
    					Person[0] = sock

    			elif Person[0] != sock:
    				a.deliver_player(socket, "You answered too late so it does not count!")


    client_socket.close()
    sock.close()
