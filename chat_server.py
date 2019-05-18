
"""
Created on Tue Jul 22 00:47:05 2014
@author: alina, zzhang
"""

import time
import socket
import select
import sys
import string
import indexer
import json
import pickle as pkl
from chat_utils import *
import chat_group as grp
import login_window

class Server:
    def __init__(self):
        self.new_clients = []  # list of new sockets of which the user id is not known
        self.logged_name2sock = {}  # dictionary mapping username to socket
        self.logged_sock2name = {}  # dict mapping socket to user name
        self.all_sockets = []
        self.group = grp.Group()
        # start server
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(SERVER)
        self.server.listen(5)
        self.all_sockets.append(self.server)
        # initialize past chat indices
        self.indices = {}
        # sonnet
        self.sonnet = indexer.PIndex("AllSonnets.txt")
        self.users = self.get_users()
        
    def get_users(self):
        temp_str = ""
        file = open("up3_user_database.txt", "r")
        for line in file:
            temp_str += line.strip()
        file.close()
        temp_dic = json.loads(temp_str)
        return temp_dic 
    
    def window_login(self,sock):
        #laod in msg
        #check if in our dictionary of users
        #return soemthing conditional on if msg is in dictionary
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:
            
                if msg["action"] == "login":
                    print("got this far - 69")
                    
                    if self.users[msg["name"]] == msg["password"]:
                        print('works up to here')
                        name = msg["name"]
                        #remove from new_clients so they are not relogged in
                        self.new_clients.remove(sock)
                        #add to these dictionaries to use later
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        print('also here')
                        if name not in self.indices.keys():
                            print('3')
                            try:
                                self.indices[name] = pkl.load(open(name + '.idx', 'rb'))
                                
                            except IOError:  # chat index does not exist, then create one
                                self.indices[name] = indexer.Index(name)
                        self.group.join(name)
                        mysend(sock, json.dumps({"action": "login", "status": "success"}))
                        
#                    elif self.users[msg["name"]] != msg["password"]:
                    else:
                        mysend(sock,json.dumps({"action":"login", "status":"error","errormsg":"login error.\nTry again, or register an account."}))
                        
                        #ignore, for self
                        print('ok done - error1') 
                        print(msg["name"])
                        print(type(self.users.keys()))
                        print(self.users.keys())
                        
                        if msg["name"] in self.users.keys():
                            print('line 100 works')
                        else:
                            print('idk')
                            
                    #ignore this
#                    elif msg["name"] not in self.users.keys():
#                        print('got this far - 97')
#                        mysend(sock,json.dumps({"action":"login", "status":"error","errormsg":"Username not recognized.\nPlease register an account."}))
##                        self.all_sockets.remove(sock)
##                        self.new_clients.remove(sock)
#                        print('ok done - error2')
#                        
#                    else:
#                        mysend(sock,json.dumps({"action":"login", "status":"error","errormsg":"IDK what is going on"}))
##                        self.all_sockets.remove(sock)
##                        self.new_clients.remove(sock)
#                        print('ok done - error3')
                
                elif msg["action"] == "register":
                    print('works up to here - 115')
                    
                    if msg["name"] in self.users.keys():
                        mysend(sock,json.dumps({"action":"register","status":"error","errormsg":"this username alreay exists, please try another."}))
                        print("ok done - error1")
                        
                    elif msg["password"] != msg["cpassword"]:
                        mysend(sock,json.dumps({"action":"register","status":"error","errormsg":"Passwords do not match, please try again"}))
                        print("ok done - error2")
                   
                    else:
                        self.users[msg["name"]] = msg["password"]
                        print(self.users)
                        file = open("up3_user_database.txt","w")
                        self.users = json.dumps(self.users)
                        file.write(self.users)
                        file.close()
                        self.users = self.get_users()
                        mysend(sock,json.dumps({"action":"register","status":"success","msg":"Registration successful! Please log in."}))      
                else:
                    self.logout(sock)
                    print("client died unexpectadly")
        except:
            pass

    def new_client(self, sock):
        # add to all sockets and to new clients
        print('new client...')
        sock.setblocking(0)
        self.new_clients.append(sock)
        self.all_sockets.append(sock)

    def login(self, sock):
        # read the msg that should have login code plus username
        try:
            msg = json.loads(myrecv(sock))
            if len(msg) > 0:

                if msg["action"] == "login":
                    name = msg["name"]
                    if self.group.is_member(name) != True:
                        # move socket from new clients list to logged clients
                        self.new_clients.remove(sock)
                        # add into the name to sock mapping
                        self.logged_name2sock[name] = sock
                        self.logged_sock2name[sock] = name
                        # load chat history of that user
#                        if name not in self.indices.keys():
#                            try:
#                                self.indices[name] = pkl.load(
#                                    open(name + '.idx', 'rb'))
#                            except IOError:  # chat index does not exist, then create one
#                                self.indices[name] = indexer.Index(name)
                        print(name + ' logged in')
                        self.group.join(name)
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "ok"}))
                    else:  # a client under this name has already logged in
                        mysend(sock, json.dumps(
                            {"action": "login", "status": "duplicate"}))
                        print(name + ' duplicate login attempt')
                else:
                    print('wrong code received')
            else:  # client died unexpectedly
                self.logout(sock)
        except:
            self.all_sockets.remove(sock)

    def logout(self, sock):
        # remove sock from all lists
        name = self.logged_sock2name[sock]
  #      pkl.dump(self.indices[name], open(name + '.idx', 'wb'))
  #      del self.indices[name]
        del self.logged_name2sock[name]
        del self.logged_sock2name[sock]
        self.all_sockets.remove(sock)
        self.group.leave(name)
        sock.close()

# ==============================================================================
# main command switchboard
# ==============================================================================
    def handle_msg(self, from_sock):
        # read msg code
        msg = myrecv(from_sock)
        if len(msg) > 0:
            # ==============================================================================
            # handle connect request this is implemented for you
            # ==============================================================================
            msg = json.loads(msg)
            if msg["action"] == "connect":
                to_name = msg["target"]
                from_name = self.logged_sock2name[from_sock]
                if to_name == from_name:
                    msg = json.dumps({"action": "connect", "status": "self"})
                # connect to the peer
                elif self.group.is_member(to_name):
                    to_sock = self.logged_name2sock[to_name]
                    self.group.connect(from_name, to_name)
                    the_guys = self.group.list_me(from_name)
                    msg = json.dumps(
                        {"action": "connect", "status": "success"})
                    for g in the_guys[1:]:
                        to_sock = self.logged_name2sock[g]
                        mysend(to_sock, json.dumps(
                            {"action": "connect", "status": "request", "from": from_name}))
                else:
                    msg = json.dumps(
                        {"action": "connect", "status": "no-user"})
                mysend(from_sock, msg)

# keys
            elif msg["action"] == "key": 
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(msg))
            elif msg["action"] == "reset":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(msg))
# ==============================================================================
# handle messeage exchange: IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "exchange":
                from_name = self.logged_sock2name[from_sock]
                """
                Finding the list of people to send to and index message
                """
                # IMPLEMENTATION
                # ---- start your code ---- #
                the_guys = self.group.list_me(from_name)
#                said2 = text_proc(msg["message"], from_name)
#                self.indices[from_name].add_msg_and_index(said2)

                # ---- end of your code --- #

                for g in the_guys[1:]:
                    to_sock = self.logged_name2sock[g]
                    # IMPLEMENTATION
                    # ---- start your code ---- #
#                    self.indices[g].add_msg_and_index(said2)
                    mysend(to_sock, json.dumps({"action":"exchange", "from":msg["from"], "message":msg["message"]}))

                    # ---- end of your code --- #

# ==============================================================================
# the "from" guy has had enough (talking to "to")!
# ==============================================================================
            elif msg["action"] == "disconnect":
                from_name = self.logged_sock2name[from_sock]
                the_guys = self.group.list_me(from_name)
                self.group.disconnect(from_name)
                the_guys.remove(from_name)
                if len(the_guys) == 1:  # only one left
                    g = the_guys.pop()
                    to_sock = self.logged_name2sock[g]
                    mysend(to_sock, json.dumps(
                        {"action": "disconnect", "message": "everyone left, you are alone"}))
# ==============================================================================
#                 listing available peers: IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "list":

                # IMPLEMENTATION
                # ---- start your code ---- #
                from_name = self.logged_sock2name[from_sock]
                msg = self.group.list_all(from_name)
                #msg = "...needs to use self.group functions to work"

                # ---- end of your code --- #
                mysend(from_sock, json.dumps(
                    {"action": "list", "results": msg}))
# ==============================================================================
#             retrieve a sonnet : IMPLEMENT THIS
# ==============================================================================
            elif msg["action"] == "poem":

                # IMPLEMENTATION
                # ---- start your code ---- #
                poem_indx = int(msg["target"])
                from_name = self.logged_sock2name[from_sock]
                print(from_name + ' asks for ', poem_indx)
                poem = self.sonnet.get_poem(poem_indx)
                poem = '\n'.join(poem).strip()
                #poem = "...needs to use self.sonnet functions to work"
                print('here:\n', poem)

                # ---- end of your code --- #

                mysend(from_sock, json.dumps(
                    {"action": "poem", "results": poem}))
# ==============================================================================
#                 time
# ==============================================================================
            elif msg["action"] == "time":
                ctime = time.strftime('%d.%m.%y,%H:%M', time.localtime())
                mysend(from_sock, json.dumps(
                    {"action": "time", "results": ctime}))
# ==============================================================================
#                 search: : IMPLEMENT THIS
# ==============================================================================#
#            elif msg["action"] == "search":

                # IMPLEMENTATION
               # ---- start your code ---- #
#                term = msg["target"]
#                from_name = self.logged_sock2name[from_sock]
                #search_rslt = "needs to use self.indices search to work"
#                search_rslt = '\n'.join([x[-1] for x in self.indices[from_name].search(term)])
#                print('server side search: ' + search_rslt)

                # ---- end of your code --- #
#                mysend(from_sock, json.dumps(
#                    {"action": "search", "results": search_rslt}))

# ==============================================================================
#                 the "from" guy really, really has had enough
# ==============================================================================

        else:
            # client died unexpectedly
            self.logout(from_sock)

# ==============================================================================
# main loop, loops *forever*
# ==============================================================================

    def run(self):
        print('starting server...')
        while(1):
            read, write, error = select.select(self.all_sockets, [], [])
            #all_sockets has the server and the sockets
            print('checking logged clients..')
            for logc in list(self.logged_name2sock.values()):
                if logc in read:
                    self.handle_msg(logc)
            print('checking new clients..')
            #new_clients has just sockets
            #might have to make a new socket for each iteration
            #each tiem you go through, tries to read recv msg
            for newc in self.new_clients[:]:
                if newc in read:
                    self.window_login(newc)
            print('checking for new connections..')
            if self.server in read:
                # new client request
                sock, address = self.server.accept()
                self.new_client(sock)



def main():
    server = Server()
    server.run()


if __name__ == '__main__':
    main()
