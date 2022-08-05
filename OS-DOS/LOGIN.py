from security import CheckPassword, GetUser
import os

def login():
    user = input('Username: ')
    passw = input('Password: ')
    if CheckPassword(passw) and user == GetUser():
        os.system('cls')
        print('Login Successful')
        print('Welcome ' + user)
        del passw, user
        import kernel # evil import hack (runs the shell)
    
    else:
        os.system('cls')
        print('Login Failed')
        input('press enter to continue . . .')
        os.system('cls')
        login() # recursive call