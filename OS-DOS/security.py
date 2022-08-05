def CheckPassword(password):
    f = open('./FILES/sys/com/meta/userdata/pass', 'r')
    passw = f.readline()
    f.close()
    del f
    if passw == password:
        del passw, password
        return True
    else:
        del passw, password
        return False

def GetUser():
    f = open('./FILES/sys/com/meta/userdata/user', 'r')
    user = f.readline()
    f.close()
    del f
    return user.strip('\n')

def SetUser(k):
    f = open('./FILES/sys/com/meta/userdata/user', 'w')
    f.write(k)
    f.close()
    del f


def SetPass(p):
    f = open('./FILES/sys/com/meta/userdata/pass', 'w')
    f.write(p)
    f.close()
    del f



def isFileProtected(path):
    f = open('./FILES/sys/com/meta/sec/protf.cnf', 'r')
    prots = f.readlines()
    f.close()
    del f
    for prot in prots:
        if prot.strip('\n') == path:
            return True
    return False
    