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


    def increment_clock(self):
        '''
        Increments the vector time index of the
        current process.
        :return: None
        :rtype: None
        '''
        self.vector_time[self.vector_index] += 1


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



        pass

    def handle_deposit(self, message_dict):
        '''
        Deposits an amount of money either recieved form another pro
        cess or independently.
        :param message_dict:
        :type message_dict:
        :return:
        :rtype:
        '''

        pass

    def send_money(self):
        '''
        Sends an amount of money to another proccess.
        The amount is randomly chosen and is always within 100.
        :return:
        :rtype:
        '''
        amount = random.randint(1,100)
        request = 'DEPO'
        random_peer_choice_index = random.randint(0,len(self.PEER_LIST)-1)
        random_peer_choice = self.PEER_LIST[random_peer_choice_index]
        #obtain access token
        self.access_lock.acquire()

        self.increment_clock()
        current_time = self.vector_time
        self.balance -= amount

        #release access token
        self.access_lock.release()

        message_dict = {'amount':amount,
                        'sender':socket.getfqdn(),
                        ''}


    def withdraw_money(self):
        '''
        Withdraws an amount of money from the account.
        The amount is randomly chosen and is always within 100.
        :return: None
        :rtype: None
        '''

        pass



