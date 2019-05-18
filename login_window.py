import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QCoreApplication
import registration_window
from client_window import *
import argparse
from chat_utils import *
import socket
login_msg = ""
import threading

#
class login(QWidget):

    def __init__(self,socket):
        super().__init__()
        
        self.socket = socket
        self.state = S_OFFLINE
        self.system_msg = "~ET CHAT~\n"
        self.login_window()
#        self.cw = client(self.socket,self.user_input.text()) 
        
        
    def login_window(self):
#        set the dimensions to the window and the title
        
        global login_msg
        self.title = 'E.T. CHAT'
        self.left = 500
        self.top = 200
        self.width = 250
        self.height = 150
        
        # get username and password as well as the buttons
        greeting = QLabel('Welcome to E.T. CHAT!\n')
        user_label = QLabel('Username:')
        self.user_input = QLineEdit()
        pw_label = QLabel('Password:')
        self.pw_input = QLineEdit()
        self.pw_input.setEchoMode(self.pw_input.Password)
        login_button = QPushButton('login')
        register_button = QPushButton('register')
        
        #get our ET picture and scale it
        pic_label = QLabel()
        pixmap = QPixmap('ET.jpeg').scaled(210,120)
        pic_label.setPixmap(pixmap)
        
        
        #put everything in our layout via rows
        self.layout = QFormLayout()
        self.layout.addRow(pic_label)
        self.layout.addRow(greeting)
        self.layout.addRow(user_label, self.user_input)
        self.layout.addRow(pw_label, self.pw_input)
        self.layout.addRow(login_button,register_button)
        
        
        #what buttons do if clicked
        register_button.clicked.connect(self.open_registration)
        login_button.clicked.connect(self.open_client)

        
        #use our setters to place everything in window
        self.setLayout(self.layout)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top,self.width, self.height)
        
        self.show() #shows our window. our self is a QWidget

        
    def open_registration(self):
        #pass socket to register, open register window
        self.r = registration_window.register(self.socket)
        self.r.show()
        self.hide()
        
#    def quit(self):
#        self.socket.shutdown(socket.SHUT_RDWR)
#        self.socket.close()
   
    def recv(self):
        return myrecv(self.socket)
    
    
    def send(self,msg):
        #send needs to send a dic in form of a dump
        mysend(self.socket, msg)
        
        
        
    def client_w(self):

        self.cw = client(self.socket,self.user_input.text()) 
        self.cw.client_window()

        
    def run_chat(self):
        self.cw.run_chat()
        
    #opens a chat window when login, or displays error message
    def open_client(self):
        global login_msg
        
        lgn_info = json.dumps({"action":"login", "name":self.user_input.text(), "password":self.pw_input.text()})
        self.send(lgn_info)
        response = json.loads(self.recv())
        if response["status"] == "success":
            
            print("status success")
            
            self.client_w()
#            self.window_thread = threading.Thread(target=self.client_thread())
#            self.window_thread.daemon = True
#            self.window_thread.start()

#            self.peer_thread = threading.Thread(target=self.run_chat())
#            self.window_thread.daemon = True
#            self.window_thread.start()



#            self.client_thread()
            self.hide()
            
        elif response["status"] == "error":
            
            print("status error")
            login_msg = response["errormsg"]
            print(login_msg)
            login_btn_response = QLabel(login_msg)
            login_btn_response.setStyleSheet("color: red;")
            self.layout.addRow(login_btn_response)
            



       
if __name__ == '__main__':
    #code for socket
    parser = argparse.ArgumentParser(description='chat client argument')
    parser.add_argument('-d', type=str, default=None, help='server IP addr')
    args = parser.parse_args()
    
    #more code for socket
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
    svr = SERVER if args.d == None else (args.d, CHAT_PORT)
    socket.connect(svr)
    
    #code for window
    login_app = QApplication(sys.argv)
    start_login = login(socket)
    sys.exit(login_app.exec_()) #do I need this?
    
