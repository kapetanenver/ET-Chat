"""
Created on Sun Apr  5 00:00:32 2015
@author: zhengzhang
"""
from chat_utils import *
import json
import rsa 
import indexer
import pickle as pkl

class ClientSM:
    def __init__(self, s):
        self.state = S_OFFLINE
        self.peer = ''
        self.me = ''
        self.out_msg = ''
        self.s = s
        self.public_key=()
        self.private_key=()
        self.peer_key=()
        self.indices = {}
        
    def set_state(self, state):
        self.state = state

    def get_state(self):
        return self.state

    def set_myname(self, name):
        self.me = name

    def get_myname(self):
        return self.me

    def connect_to(self, peer):
        msg = json.dumps({"action":"connect", "target":peer})
        mysend(self.s, msg)
        response = json.loads(myrecv(self.s))
        if response["status"] == "success":
            self.peer = peer
            self.out_msg += 'You are connected with '+ self.peer + '\n'
            return (True)
        elif response["status"] == "busy":
            self.out_msg += 'User is busy. Please try again later\n'
        elif response["status"] == "self":
            self.out_msg += 'Cannot talk to yourself (sick)\n'
        else:
            self.out_msg += 'User is not online, try again later\n'
        return(False)

    def disconnect(self):
        msg = json.dumps({"action":"disconnect"})
        mysend(self.s, msg)
        self.out_msg += 'You are disconnected from ' + self.peer + '\n'
        self.peer = ''
        
    def reset_keys(self):
        self.public_key=()
        self.private_key=()
        self.peer_key=()
        
    def set_indexing(self):
        if self.me not in self.indices.keys():
            try:
                self.indices[self.me] = pkl.load(
                        open(self.me + '.idx', 'rb'))
            except IOError:  # chat index does not exist, then create one
                self.indices[self.me] = indexer.Index(self.me)
                
    def proc(self, my_msg, peer_msg):
        self.out_msg = ''
        self.set_indexing()
    
#==============================================================================
# Once logged in, do a few things: get peer listing, connect, search
# And, of course, if you are so bored, just go
# This is event handling instate "S_LOGGEDIN"
#==============================================================================
        if self.state == S_LOGGEDIN:
            # todo: can't deal with multiple lines yet
            if len(my_msg) > 0:
                
                if my_msg == 'q':
                    self.out_msg += 'See you next time!\n'
                    pkl.dump(self.indices[self.me], open(self.me + '.idx', 'wb'))
                    del self.indices[self.me]
                    self.state = S_OFFLINE

                elif my_msg == 'time':
                    mysend(self.s, json.dumps({"action":"time"}))
                    time_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += "Time is: " + time_in

                elif my_msg == 'who':
                    mysend(self.s, json.dumps({"action":"list"}))
                    logged_in = json.loads(myrecv(self.s))["results"]
                    self.out_msg += 'Here are all the users in the system:\n'
                    self.out_msg += logged_in

                elif my_msg[0] == 'c':
                    peer = my_msg[1:]
                    peer = peer.strip()
                    if self.connect_to(peer) == True:
                        self.state = S_CHATTING
                        self.out_msg += 'Connect to ' + peer + '. Chat away!\n\n'
                        self.out_msg += '-----------------------------------\n'
                    else:
                        self.out_msg += 'Connection unsuccessful\n'

                elif my_msg[0] == '?':
                    term = my_msg[1:].strip()
                    rslt = '\n'.join([x[-1] for x in self.indices[self.me].search(term)])
                    #mysend(self.s, json.dumps({"action":"search", "target":term}))
                    #search_rslt = json.loads(myrecv(self.s))["results"].strip()
                    if (len(rslt)) > 0:
                        self.out_msg += rslt + '\n\n'
                    else:
                        self.out_msg += '\'' + term + '\'' + ' not found\n\n'

                elif my_msg[0] == 'p' and my_msg[1:].isdigit():
                    poem_idx = my_msg[1:].strip()
                    mysend(self.s, json.dumps({"action":"poem", "target":poem_idx}))
                    poem = json.loads(myrecv(self.s))["results"]
                    if (len(poem) > 0):
                        self.out_msg += poem + '\n\n'
                    else:
                        self.out_msg += 'Sonnet ' + poem_idx + ' not found\n\n'

                else:
                    self.out_msg += menu

            if len(peer_msg) > 0:
                try:
                    peer_msg = json.loads(peer_msg)
                except Exception as err :
                    self.out_msg += " json.loads failed " + str(err)
                    return self.out_msg

                if peer_msg["action"] == "connect":
                    # ----------your code here------#
                    self.peer = peer_msg["from"]
                    self.out_msg += 'Request from ' + self.peer + '\n'
                    self.out_msg += 'You are connected with ' + self.peer
                    self.out_msg += '. Chat away!\n\n'
                    self.out_msg += '------------------------------------\n'
                    self.state = S_CHATTING
                    # ----------end of your code----#

#==============================================================================
# Start chatting, 'bye' for quit
# This is event handling instate "S_CHATTING"
#==============================================================================
        elif self.state == S_CHATTING:
            if self.public_key == ():
                self.public_key, self.private_key = rsa.generate_keys()
                mysend(self.s, json.dumps({"action" :"key", "public key" : self.public_key}))
            if len(my_msg) > 0:     # my stuff going out
                msg = rsa.encrypt(my_msg, self.private_key)
                said2 = text_proc(my_msg, self.me)
                self.indices[self.me].add_msg_and_index(said2)
                mysend(self.s, json.dumps({"action":"exchange", "from":  self.me   , "message":msg}))
                self.out_msg += "[" + self.me + "] " + my_msg + "\n"
                if my_msg == 'bye':
                    mysend(self.s, json.dumps({"action" :"reset"}))
                    self.disconnect()
                    self.state = S_LOGGEDIN
                    self.peer = ''
                    self.reset_keys()
    
            if len(peer_msg) > 0:  # peer's stuff, coming in
                # ----------your code here------#
                peer_msg = json.loads(peer_msg)
                if peer_msg["action"] == "connect":
                    self.out_msg += "(" + peer_msg["from"] + " joined)\n"
                elif peer_msg["action"] == "disconnect":
                    self.state = S_LOGGEDIN
                elif peer_msg["action"] == "key":
                    self.peer_key = peer_msg["public key"]
                elif peer_msg["action"] == "exchange":
                    msg = rsa.encrypt(peer_msg["message"], self.peer_key)
                    self.out_msg += "Encrypted message:" + peer_msg['message'] +'\n'
                    self.out_msg += "["+ peer_msg["from"] + "]"  + msg
                    said2 = text_proc(msg, peer_msg["from"])
                    self.indices[self.me].add_msg_and_index(said2)
                elif peer_msg["action"] == "reset":
                    self.reset_keys()
                # ----------end of your code----#
            if self.state == S_LOGGEDIN:
                # Display the menu again
                self.out_msg += menu
#==============================================================================
# invalid state
#==============================================================================
        else:
            self.out_msg += 'How did you wind up here??\n'
            print_state(self.state)

        return self.out_msg
