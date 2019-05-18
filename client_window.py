import sys
import time
import json
import socket
import select
import threading
from PyQt5.QtWidgets import *
from chat_utils import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
import client_state_machine as csm


#import login_window
#import registration_window


class client(QWidget):
    def __init__(self, socket, name):
        super().__init__()
        
        self.socket = socket
        self.name = name
        self.state = S_LOGGEDIN
        self.sm = csm.ClientSM(self.socket)
        self.system_msg = ""
        self.k_input = []
        self.display = QTextEdit()
        self.keyboard = QLineEdit()
        self.sm.set_state(self.state)
        self.sm.set_myname(self.name)
        
#        self.client_window()
#        self.run_chat()
#        self.reading_thread = threading.Thread(target=self.get_peer_msg())
#        self.reading_thread.daemon = True
#        self.reading_thread.start()
        #add threading for peer msg
        #add threading for displaying msg
        
        #DOES NOT WORK IF BELOW RAN
        #self.get_peer_msg()

        
    def client_window(self):
        
        #create dimensions and title of window
        self.title = 'ET CHAT'
        self.left = 500
        self.top = 200
        self.width = 450
        self.height = 500
        
        # display screen
        self.display = self.display
        self.system_msg += '~ET CHAT~\n' + 'Welcome, ' + self.name + '!\n' + menu
        welcome_msg = self.system_msg.split('\n')
        self.system_msg = ""
        
        for i in welcome_msg:
            self.display.append(i)
        self.display.setReadOnly(True)
        
        #input
        self.horizontal_input()

        #handle button push
        self.send_button.clicked.connect(self.update_msg)
        
        
        #create the layout of the window
        layout = QVBoxLayout()
        layout.addWidget(self.display)
        layout.addWidget(self.horizontalGroupBox)
        

        #set the layout to the window
        self.setLayout(layout)       
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.setWindowTitle(self.title)
        
        self.show()
        
#        while self.sm.get_state() != S_OFFLINE:
#            self.proc()
#            self.output()
#            time.sleep(CHAT_WAIT)
#        self.quit()

    # creates keyboard/send button
    def horizontal_input(self):
        #groups together keyboard and send button
        self.horizontalGroupBox = QGroupBox()
        layout = QHBoxLayout()
        
        self.keyboard = self.keyboard
        self.send_button = QPushButton('send')
        layout.addWidget(self.keyboard)
        layout.addWidget(self.send_button)
        
        self.horizontalGroupBox.setLayout(layout)
    
    
    #get user input
    def update_msg(self):
        text = self.keyboard.text()
        self.k_input.append(text) # no need for lock, append is thread safe
        self.keyboard.clear()
        print(self.sm.get_state())
#        self.proc()
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += self.sm.proc(my_msg, peer_msg)
        self.output()
        time.sleep(CHAT_WAIT)
        
        
    def run_chat(self):
        while self.sm.get_state() != S_OFFLINE:
            self.proc()
            self.output()
            time.sleep(CHAT_WAIT)
        self.quit()
        
        print(self.sm.get_state())
        self.proc()
#        my_msg, peer_msg = self.get_msgs()
#        self.system_msg += self.sm.proc(my_msg, peer_msg)
        self.output()
        time.sleep(CHAT_WAIT)
          
           
    #get peer msg
    
#    def get_peer_msg(self):
#        while self.sm.get_state() != S_OFFLINE:
#            try:
#                my_msg, peer_msg = self.get_msgs()
#                if len(peer_msg) > 0:
#                    self.system_msg += self.sm.proc(my_msg, peer_msg)
#                    self.output()
#                    time.sleep(CHAT_WAIT)
#                    
#            except:
#                pass
#        self.quit()
    
    #quits the program
    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.hide()

    def recv(self):
        return myrecv(self.socket)

    
    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = [] #does this have to be a list?
#        k_input = self.update_msg()
        if len(self.k_input) > 0:
            my_msg = self.k_input.pop(0) # do I need to clear this variable everytime a user types smth? does the textbox clear?
            print(my_msg)
        if self.socket in read:
            peer_msg = self.recv()
            
        return my_msg, peer_msg
    
    def output(self):
#        temp_msg = self.system_msg.split("\n")
#        for i in temp_msg:   
        self.display.append(self.system_msg)
        self.system_msg = ""
    
    
    # gets msgs to send to state machine
    # from state machine gets appropriate output to display
    def proc(self):
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += self.sm.proc(my_msg, peer_msg)
    

#    def run_chat(self):
#        
##        self.cw = self.client_window()
#        self.reading_thread = threading.Thread(target=self.update_msg)
#        self.reading_thread.daemon = True
#        self.reading_thread.start()
#        self.sm.set_state(self.state)
#        self.sm.set_myname(self.name)
#        while self.sm.get_state() != S_OFFLINE:
#            print("working?")
#            self.proc()
#            self.output()
#            time.sleep(CHAT_WAIT)
#        self.quit()
#
#



if __name__ == '__main__':
    client_app = QApplication(sys.argv)
    start_client = client()
#    start_client.show()
    sys.exit(client_app.exec())
