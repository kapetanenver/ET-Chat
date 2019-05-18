import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap
from login_window import login

class register(QWidget):
    
    def __init__(self):
        super().__init__()
        
#        self.title = 'ET CHAT'
#        self.left = 300
#        self.top = 100
#        self.width = 250
#        self.height = 150
        
        self.register_window()


    def register_window(self):
        
        self.title = 'ET CHAT'
        self.left = 500
        self.top = 200
        self.width = 250
        self.height = 150
        
        greeting = QLabel('Please Register Your New Account Below' + '\n')
        user_label = QLabel('New Username:')
        user_input = QLineEdit()
        pw_label = QLabel('New Password:')
        pw_input = QLineEdit()
        pw_input.setEchoMode(pw_input.Password)
        cpw_label = QLabel('Confirm New Password:')
        cpw_input = QLineEdit()
        cpw_input.setEchoMode(cpw_input.Password)
        return_button = QPushButton('back to login')
        submit_button = QPushButton('submit')
        
        #what to do if buttons clicked
        return_button.clicked.connect(self.back_to_login)
        
        layout = QFormLayout()
        layout.addRow(greeting)
        layout.addRow(user_label, user_input)
        layout.addRow(pw_label, pw_input)
        layout.addRow(cpw_label, cpw_input)
        layout.addRow(return_button, submit_button)
        
        self.setLayout(layout)
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()
        
    def back_to_login(self):
        self.l = login()
        self.hide()
        


if __name__ == '__main__':
    register_app = QApplication(sys.argv)
    ex = register()
    sys.exit(register_app.exec_())
