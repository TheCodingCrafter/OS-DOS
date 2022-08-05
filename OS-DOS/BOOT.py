import time
import drivers
import LOGIN
import os

StartupMsg = '''
select a boot option:
[1] boot normally
[2] configure BIOS
[3] shutdown
'''

BIOS_msg = '''
select a BIOS option:
    [1] change BIOS password
    [2] optimize boot time = {opti}
    [3] exit
'''

KEYBOARD = drivers.KeyboardDriver()
DISPLAY = drivers.ScreenDriver()

def print(msg, end='\n'):
    DISPLAY.display(msg, end)

def BOOT():
    print(StartupMsg)
    inpt = KEYBOARD.GetInpt('> ')
    if inpt == '1':
        print('booting from hard disk . . .')
        # read opti from file
        f = open('./FILES/sys/com/bios/bto.cnf', 'r')
        opti = f.readline()
        f.close()
        del f
        if opti == '1':
            time.sleep(1)
        elif opti == '0':
            time.sleep(7)
        os.system('cls')
        LOGIN.login()
        
    elif inpt == '2':
        os.system('cls')
        # confirm bios password
        print('enter BIOS password:')
        p = KEYBOARD.GetInpt('> ')
        # read pass (./FILES/sys/com/bios/bpw.cnf)
        f = open('./FILES/sys/com/bios/bpw.cnf', 'r')
        passw = f.readline()
        f.close()
        del f
        if passw == p:
            # config bios
            # read opti (./FILES/sys/com/bios/bto.cnf)
            f = open('./FILES/sys/com/bios/bto.cnf', 'r')
            opti = f.readline()
            f.close()

            opti = opti.strip('\n') == '1'
            os.system('cls')
            print(BIOS_msg.format(opti=opti))

            inpt = KEYBOARD.GetInpt('> ')
            if inpt == '1':
                os.system('cls')
                # change password
                print('enter new password:')
                p = KEYBOARD.GetInpt('> ')
                f = open('./FILES/sys/com/bios/bpw.cnf', 'w')
                f.write(p)
                f.close()
                print('password changed')
                del f, p
                input('press enter to continue . . .')
                os.system('cls')
                BOOT()
            
            elif inpt == '2':
                os.system('cls')
                # optimize boot time
                print('enter whether to optimize boot time(y/n):')
                inpt = KEYBOARD.GetInpt('> ')
                if inpt == 'y':
                    time.sleep(3)
                    f = open('./FILES/sys/com/bios/bto.cnf', 'w')
                    f.write('1')
                    f.close()
                    print('enabled boot optimization')
                    input('press enter to continue . . .')
                    os.system('cls')
                    BOOT()

                elif inpt == 'n':
                    time.sleep(3)
                    f = open('./FILES/sys/com/bios/bto.cnf', 'w')
                    f.write('0')
                    f.close()
                    print('disabled boot optimization')
                    input('press enter to continue . . .')
                    os.system('cls')
                    BOOT()
                del f, inpt
            
            elif inpt == '3':
                # exit
                os.system('cls')
                BOOT()

        else:
            print('wrong password')
            input('press enter to continue . . .')
            os.system('cls')
            BOOT()

    elif inpt == '3':
        os.system('cls')
        print('shutting down . . .')
        time.sleep(2)
        exit()
BOOT()