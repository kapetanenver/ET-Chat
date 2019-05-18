#OUR IMPLEMENTATIONS


#LOGIN SYSTEM
'''
For the login system what we did was create a dictionary that holds all
the usernames and passwords together that have been logged in before.
You start the program by running the login window, and from there may enter
the registration window if you do not have an account, or you may
directly enter the chat window if you have an account. When there is an error
from registering an account or loginng into the system, and error msg is
display and the client is prompted to try again.
'''

#GUI
'''
So technically we made three GUI windows: the registration window,the login
window, and the client window. We struggled to make the client window
optimal, however it is fully functional. In order to get msgs from other
peers a client must first hit the send button. This is bad design,
we are aware, but could not figure out how to implement a thread that
ran a while loop to check for peer msgs while running the window. This is
something we want to fix in the future. Aside from this kink however,
all of our GUIs run fine, and the menu commands all work the same.
'''




#ENCRYPTION
'''
For the encryption we used the RSA encryption method. Firstly I created a file that holds all functions related to creating the keys and encrypting the files. Secondly I imported these files into the client state machine and created new actions to send the public keys out to the other user when chatting. The public key is used to encrypt the messages sent to a user then the user uses their own private key to decrypt the text. Changes also had to be made to the server to accommodate this. The search functionality wasn't working after encryption because the server couldn't read the encrypted messages so we had to move the search functionality to the clients side. This was done by storing individual user history on their own computer, and conducting the search through the client state machine. 