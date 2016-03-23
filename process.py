import json
import socket
import time
import random
import threading

class Process:

    '''
    One of the processes in our application.
    Has an initial balance of 1000.
    Performs one of three actions every 5 seconds:
        1. Withdraw : Withdraws money from account
        2. Send Money: Sends money to another process
        3. Deposit: Deposits money into account (independently or when
           recieved from another process).
    Each of these actions has a vector timestamp associated with it.
    This timestamp will be displayed on the console. Each process starts with
    vector time (0,0,0) (for a 3-process system).
    '''

    def __init__(self):

        self.vector_time = [0,0,0]
        self.PEER_LIST = ['glados.cs.rit.edu', 'doors.cs.rit.edu', 'hendrix.cs.rit.edu']
        self.vector_index = self.PEER_LIST.index(socket.getfqdn())
        self.balance = 1000
        self.access_lock=  threading.Lock()
        self.PORT = 23648
        listener = self.create_listener(('0.0.0.0',self.PORT))

        #Start accepting incoming connections
        thread = threading.Thread(target=self.accept_connections, args=[listener], daemon=True)
        thread.start()


    def increment_clock(self):
        '''
        Increments the vector time index of the
        current process.
        :return: None
        :rtype: None
        '''
        self.vector_time[self.vector_index] += 1

    def compare_clocks(self, other_clock):
        '''
        Compares the logical time registered for
        other processes in our vector time. Chooses
        maximum.

        :param other_clock:
        :type other_clock:
        :return:
        :rtype:
        '''
        for i in range(len(self.vector_time)):
            #Ignore our pprocess index
            if i == self.vector_index:
                pass
            #Else, choose maximum value
            else:
                self.vector_time[i]  = max(self.vector_time[i], other_clock[i])



    def create_listener(self,address):
        '''
        Creates a server socket on the specified address.

        :param address: (address,port)
        :type address: Tuple
        :return: server socket
        :rtype: Socket
        '''
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        listener.bind(address)
        listener.listen(12)
        return listener

    def accept_connections(self,listener):
        '''
        Accepts a connection and creates another thread to handle it.

        :param listener:    Our listening serversocket
        :type listener:     Socket
        :return:            None
        :rtype:             None
        '''

        while(True):
            client_socket,client_address = listener.accept()
            thread = threading.Thread(target=self.handle_connections, args=[client_socket], daemon= True)
            thread.start()


    def handle_connections(self, client_socket):
        '''
        Handles a new connection.

        :return:
        :rtype:
        '''

        request_dict = json.loads(client_socket.recv(1024).decode())
        request = request_dict['request']
        message_dict = request_dict['message']

        if request == 'DEPO':
            self.handle_deposit(message_dict)




    def handle_deposit(self, message_dict):
        '''
        Deposits an amount of money either recieved form another pro
        cess or independently.
        :param message_dict:
        :type message_dict:
        :return:
        :rtype:
        '''
        amount = message_dict['amount']
        other_clock = message_dict['time']
        sender = message_dict['sender']

        #acquire access token
        self.access_lock.acquire()

        self.increment_clock()
        self.compare_clocks(other_clock)
        event_time  = self.vector_time
        self.balance += amount
        event_balance = self.balance

        #release access token
        self.access_lock.release()

        #print message
        #Print event onto console
        print("Deposit {} from {} \n"
              "Event Balance: {} \n"
              "Event Time: {} \n"
              "********************************".format(amount, sender,
                                                        event_balance, event_time))



    def send_money(self, peer_choice = None):
        '''
        Sends an amount of money to another proccess.
        The amount is randomly chosen and is always within 100.
        :return:
        :rtype:
        '''
        amount = random.randint(1,100)
        request = 'DEPO'
        if not peer_choice:
            peers = self.PEER_LIST.copy()
            peers.remove(socket.getfqdn())
            random_peer_choice_index = random.randint(0,len(peers)-1)
            random_peer_choice = peers[random_peer_choice_index]

        else:
            random_peer_choice = peer_choice

        #obtain access token
        self.access_lock.acquire()
        if not peer_choice:
            self.increment_clock()
        current_time = self.vector_time.copy()
        if not peer_choice:
            self.balance -= amount
        event_balance = self.balance
        #release access token
        self.access_lock.release()

        message_dict = {'amount':amount,
                        'sender':socket.getfqdn(),
                        'time':current_time}
        request_dict = {'request':request,
                        'message':message_dict}
        request_blob = json.dumps(request_dict).encode()

        #Send message
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        send_sock.connect((random_peer_choice,self.PORT))
        send_sock.send(request_blob)
        send_sock.close()

        #Print event onto console
        if not peer_choice:
            print("Sent {} to {} \n"
                  "Event Balance: {} \n"
                  "Event Time: {} \n"
                  "********************************".format(amount, random_peer_choice,
                                                            event_balance, current_time))



    def withdraw_money(self):
        '''
        Withdraws an amount of money from the account.
        The amount is randomly chosen and is always within 100.
        :return: None
        :rtype: None
        '''

        pass


def do_things(process):
    while True:
        choice = random.randint(1,2)
        #Deposit
        if choice == 1:
            process.send_money(socket.getfqdn())
        #Send money
        else:
            process.send_money()
        time.sleep(5)



if __name__ == '__main__':
    process = Process()

    while True:
        n = input("Please enter 1 to start doing things")
        if n == '1':
            break
        else:
            print("Please enter 1 ")

    do_things(process)










