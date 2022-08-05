import os
import sys
import time
from CONFIG import MAIN_DRIVE_PATH, CMD, USR_HOME
import shutil
from security import CheckPassword, GetUser, SetUser, SetPass, isFileProtected
import textedit
import shlex

VAR = None
VARS = {}
LV = None

# CONFIG
def GetMaxDriveSize() -> int:
  with open(f'{MAIN_DRIVE_PATH}/sys/partition/size', 'r') as f:
    return int(f.readline().strip('\n'))

MAX_SIZE = GetMaxDriveSize()
DRIVE_SIZE = 0

def GetDriveSize(path=MAIN_DRIVE_PATH) -> int:
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += GetDriveSize(entry.path)
    return total

def UpdateDriveSize() -> None:
  global DRIVE_SIZE
  DRIVE_SIZE = GetDriveSize()

UpdateDriveSize()

def IsSpaceLeft(size) -> bool:
  UpdateDriveSize()
  return size + DRIVE_SIZE < MAX_SIZE


###############################################################################
# user stuff
###############################################################################
def user_CMD(cmd, isRoot=False) -> int:
  match cmd[1]:
    case 'chname':
      SetUser(cmd[2])
    
    case 'chpass':
      p = input(f'password for {GetUser()}: ')
      if CheckPassword(p):
        SetPass(cmd[2])
      del p 


###############################################################################
# diskmgmt stuff
###############################################################################
def diskmgmt_CMD(cmd, isRoot=False) -> int:
  match cmd[0]:
    case 'size':
      # change size in ./FILES/sys/partition/size
      if isRoot:
        with open(f'{MAIN_DRIVE_PATH}/sys/partition/size', 'w') as f:
          f.write(cmd[1])
        # update MAX_SIZE
        global MAX_SIZE
        MAX_SIZE = int(cmd[1])
        return 0
      else:
        print('Run as root to change drive size, "sudo diskmgmt"')
        return -5

###############################################################################


def GetDisplaySize(size) -> str:
  display_size = 'ERROR' # sets to error because it will be overwritten unless it isnt a valid size
  if size >= 1000000000000:
    display_size = str(round(size/1000000000000, 1)) + 'TB'

  elif size >= 1000000000 and size < 1000000000000:
    display_size = str(round(size/1000000000, 1)) + 'GB'

  elif size >= 1000000 and size < 1000000000:
    display_size = str(round(size/1000000, 1)) + 'MB'
                    
  else:
    display_size = str(round(size/1000, 1)) + 'KB'
  
  return display_size

def ExpandPath(path) -> str:
  if path[0] == '.':
    # return sys.argv[0] without kernel.py extension
    return sys.argv[0][:-10] + path[1:]
  else:
    return path

def GetPathLst(path) -> list:
  return path.split('/')

def MakePath(lst) -> str:
  v = ''
  for x in lst: v += x + '/'
  return v[:-1]

def CullPath(path) -> str:
  return './'+path[8:]

def MapError(code) -> str:
  dct = {-1: 'InputError',
        -2: 'FileOrDirectoryError',
        -3: 'RecursionError',
        -4: 'ImplementedError',
        -5: 'PermissionError',
        -6: 'PythonError',
        }
  return dct[code]

class BashProcesser:
    def __init__(self):
        self.CWD = USR_HOME
    
    def GetCwd(self):
        return self.CWD

    def ParseCmd(self, cmd):
        x = shlex.split(cmd)
        y = []
        for c in x:
          if c == '$':
            y.append(str(VAR))
          elif c == '&':
            y.append(LV)
          else:
            y.append(c.replace('\\n', '\n'))
        return y

    def command(self, cmd, isRoot=False):
      global VARS, LV
      try:
        match cmd[0]:
          # LS COMMAND
            case CMD.LS:
              print('')
              tmp = GetDriveSize()
              tmp2 = GetMaxDriveSize()

              current_display_size = GetDisplaySize(tmp)
              max_display_size = GetDisplaySize(tmp2)

              space_left = tmp2 - tmp
              space_left = GetDisplaySize(space_left)

              print(f'{current_display_size}/{max_display_size} used')
              print(f'{space_left} left')
              print('')
              for path, dirs, files in os.walk(self.CWD):
                  m = CullPath(path)

                  for file in files:
                      size = os.path.getsize(path+'/'+file)

                      print(f'FILE -- {m} -- {file} -- {GetDisplaySize(size)}')

                  for dir in dirs:
                      print(f'DIR -- {m} -- {dir}')
                  break
              print('')
              return 0
            
            # CD COMMAND
            case CMD.CD:
              try:
                if cmd[1] == '..':
                  x = GetPathLst(self.CWD)
                  x.pop(-1)
                  if x == ['.']:
                    return 0

                  else:
                    self.CWD = MakePath(x)
                    return 0
                else:
                  x = self.CWD + '/' + cmd[1]
                  if os.path.exists(x) and os.path.isdir(x):
                    self.CWD = x
                    return 0
              except IndexError:
                print('Not enough arguments')
                return -1
              
            # MKD COMMAND
            # make a directory if it does not exist realtive to self.CWD
            case CMD.MKD:
              x = self.CWD + '/' + cmd[1]
              if not os.path.exists(x):
                os.mkdir(x)
                return 0
              else:
                print('Directory already exists')
                return -2
            
            # RMD COMMAND
            # remove a directory if it exists realtive to self.CWD
            case CMD.RMD:
              x = self.CWD + '/' + cmd[1]
              if os.path.exists(x) and os.path.isdir(x):
                try:
                  os.rmdir(x)
                  return 0
                # if the directory is not empty then return -3
                except OSError:
                  if isRoot == False:
                    print('Directory is not empty\nUse "sudo rmd <dir> to recursively remove')
                  elif isRoot == True:
                    shutil.rmtree(x)
                    return 0
                  return -2

              else:
                print('Directory does not exist')
                return -2
            
            # MKF COMMAND
            # make a file if it does not exist realtive to self.CWD
            case CMD.MKF:
              x = self.CWD + '/' + cmd[1]
              if not os.path.exists(x):
                f = open(x, 'x'); f.close()
                return 0

              else:
                print('File already exists')
                return -2
            
            # RMF COMMAND
            # remove a file if it exists realtive to self.CWD
            case CMD.RMF:
              if not isFileProtected(cmd[1]) or isRoot:
                x = self.CWD + '/' + cmd[1]
                if os.path.exists(x) and os.path.isfile(x):
                  os.remove(x)
                  return 0
                else:
                  print('File does not exist')
                  return -2
              else:
                print('File is protected')
                return -2
            
            # SUDO COMMAND
            # run a command as root
            case CMD.SUDO:
              tries = 0
              MaxTries = 3
              while tries < MaxTries:
                tries += 1
                if CheckPassword(input(f'Enter password for user {GetUser()}\n: ')):
                  self.command(cmd[1:], isRoot=True)
                  return 0
                else:
                  print('Invalid Password')
              print('Too many failed attempts')
              return -3

            # HELP COMMAND
            # print help
            case CMD.HELP:
              print('')
              print('* = not implemented')
              print('')
              print('ls -- list files and directories')
              print('cd -- change directory')
              print('mkd -- make directory')
              print('rmd -- remove directory')
              print('mkf -- make file')
              print('rmf -- remove file')
              print('sudo -- run as root')
              print('help -- print help')
              print('exit -- exit')
              print('apt -- run package manager')
              print('diskmgmt -- manage disk space')
              print('whoami -- display username')
              print('touch -- display file X\'s size')
              print('cls -- clear screen')
              print('gets -- get user input')
              print('execute -- execute script X')
              print('exit -- exit')
              print('echo -- display text')
              print('echoln -- display text with newline')
              print('setv -- set variable')
              print('getv -- get variable')
              print('user -- user cmds')
              print('edit -- edit file X')
              print('cat -- display file X')
              print('dump -- dump file X -> Y')
              print('append -- append to file X')
              print('append-top -- append to top of file X')
              print('')
              return 0
            
            # EDIT COMMAND
            case CMD.EDIT:
              if not isFileProtected(self.CWD + '/' + cmd[1]) or isRoot:
                if os.path.exists(self.CWD + '/' + cmd[1]):
                  # get len of text in file
                  with open(self.CWD + '/' + cmd[1], 'r') as f:
                    text = f.read()
                    text_len = len(text)

                  textedit.openwindow(self.CWD + '/' + cmd[1], GetDriveSize(), GetMaxDriveSize(), text_len)
                  return 0
                else:
                  a = self.CWD + '/' + cmd[1]
                  print(f'no such file: {a}')
                  return -2
              else:
                print('file is protected')
                return -5
              
            # APT COMMAND
            case CMD.APT:
              print('')
              # if installing and not root
              if cmd[1] == 'install':
                if isRoot == False:
                  print('You must be root to install packages')
                  return -5
                else:
                  # if cmd[2] is a dir in PACK
                  if os.path.exists('./PACK' + '/' + cmd[2]) and os.path.isdir('./PACK' + '/' + cmd[2]):
                    # get package size
                    size = GetDriveSize(path='./PACK' + '/' + cmd[2])

                    display_size = ''
                    if size >= 1000000000000:
                      display_size = str(round(size/1000000000000, 1)) + 'TB'

                    elif size >= 1000000000 and size < 1000000000000:
                      display_size = str(round(size/1000000000, 1)) + 'GB'

                    elif size >= 1000000 and size < 1000000000:
                      display_size = str(round(size/1000000, 1)) + 'MB'
                    
                    else:
                      display_size = str(round(size/1000, 1)) + 'KB'


                    
                    q = input(f'Found package {cmd[2]}, size: {display_size}, proceed?(y/n): ')
                    if q.lower() != 'y':
                      print('Aborted')
                      return 0

                    # if size is less than max drive size
                    if size < GetMaxDriveSize():
                      # install package
                      print(f'installing {cmd[2]}')

                      src = './PACK' + '/' + cmd[2]
                      dst = './FILES/usr/lib/' + cmd[2]

                      try:
                        shutil.copytree(src, dst)
                        # copy cmd[2] + "_short.shs" to ./FILES/usr/lib
                        if os.path.exists('./PACK' + '/' + cmd[2] + '/' + f'{cmd[2]}_short.shs'):
                          shutil.copy('./PACK' + '/' + cmd[2] + '/' + f'{cmd[2]}_short.shs', './FILES/usr')
                          # remove cmd[2] + "_short.shs" from ./FILES/usr/lib
                          os.remove('./FILES/usr/lib' + '/' + cmd[2] + '/' + f'{cmd[2]}_short.shs')

                        print('done')
                        print('')
                        return 0
                        
                      except FileExistsError:
                        print('Package already installed')
                        return -2

                    else:
                      print('Not enough space left')
                      return -2
                  else:
                    print('Invalid package name')
                    return -1

              # if removing
              elif cmd[1] == 'uninstall':
                if isRoot == False:
                  print('You must be root to remove packages')
                  return -5

                else:
                  if os.path.exists(f'./FILES/usr/lib/{cmd[2]}') and os.path.isdir(f'./FILES/usr/lib/{cmd[2]}'):
                    if input(f'Are you sure you want to remove {cmd[2]}?(y/n): ').lower() == 'n':
                      print('Aborted')
                      return 0
                    print(f'removing {cmd[2]}')
                    shutil.rmtree(f'./FILES/usr/lib/{cmd[2]}')
                    # remove cmd[2] + "_short.shs" from ./FILES/usr
                    if os.path.exists('./FILES/usr' + '/' + f'{cmd[2]}_short.shs'):
                      os.remove('./FILES/usr' + '/' + f'{cmd[2]}_short.shs')
                    print('done')
                  else:
                    print('Invalid package name')
                    return -1

            
            # DISKMGMT COMMAND
            case CMD.DISKMGMT:
              print('entering disk management mode . . .')
              running = True
              while running:
                cmd = input('diskmgmt>> ')

                if cmd == 'exit':
                  running = False
                  print('exiting disk management mode . . .')
                  time.sleep(1)
                  return 0

                else:
                  err = diskmgmt_CMD(self.ParseCmd(cmd), isRoot)
                  if err != 0 and err is not None:
                    print(f'Diskmgmt Error {err} | {MapError(err)}')
                    return 0
              return 0
            
            # WHOAMI COMMAND
            case CMD.WHOAMI:
              print(GetUser())
              return 0
            
            # TOUCH COMMAND
            case CMD.TOUCH:
              if os.path.exists(self.CWD + '/' + cmd[1]):
                s = os.path.getsize(self.CWD + '/' + cmd[1])
                print(f'size of {cmd[1]} is {s} bytes')
            
            # CLS COMMAND
            case CMD.CLS:
              os.system('cls')
            
            # EXECUTE COMMAND
            case CMD.EXECUTE:
              error = 0
              # if cmd[1] is a file then run it using self.command
              if os.path.exists(self.CWD + '/' + cmd[1]) and os.path.isfile(self.CWD + '/' + cmd[1]):
                with open(self.CWD + '/' + cmd[1], 'r') as f:
                  for line in f:
                    cmd = self.ParseCmd(line)
                    err = self.command(cmd)

                    if err != 0 and err is not None:
                      print(f'Script Error {err} | {MapError(err)}')
                      error = err

                return error
            
            # GETS COMMAND
            case CMD.GETS:
              if len(cmd) > 1:
                global VAR
                VAR = '"' + input(cmd[1]) + '"'
            
            # CAT COMMAND
            case CMD.CAT:
              if not isFileProtected(self.CWD + '/' + cmd[1]) or isRoot:
                if os.path.exists(self.CWD + '/' + cmd[1]):
                  with open(self.CWD + '/' + cmd[1], 'r') as f:
                    print('')
                    for i, line in enumerate(f):
                      v = line.strip('\n')
                      print(f'{i+1} {v}')
                    print('')
                else:
                  print('File does not exist')
                  return -1
              else:
                print('File is protected')
                return -5
              
            # APPEND COMMAND
            case CMD.APPEND:
              if not isFileProtected(self.CWD + '/' + cmd[1]) or isRoot:
                if os.path.exists(self.CWD + '/' + cmd[1]):
                  with open(self.CWD + '/' + cmd[1], 'a') as f:
                    f.write(cmd[2]+'\n')
                else:
                  print('File does not exist')
                  return -1
              else:
                print('File is protected')
                return -5
            
            # APPEND_TOP COMMAND
            case CMD.APPEND_TOP:
              if not isFileProtected(self.CWD + '/' + cmd[1]) or isRoot:
                if os.path.exists(self.CWD + '/' + cmd[1]):
                  with open(self.CWD + '/' + cmd[1], 'r') as f:
                    bottom = f.read()
                  with open(self.CWD + '/' + cmd[1], 'w') as f:
                    f.write(cmd[2] + '\n' + bottom)
                else:
                  print('File does not exist')
                  return -1
              else:
                print('File is protected')
                return -5

            # LOOP COMMAND
            case CMD.LOOP:
              for i in range(int(cmd[1])):
                self.command(cmd[2:])
            
            # IF COMMAND
            case CMD.IF:
              lst = []
              lst2 = []
              # loop through cmd and append to lst until we hit "then" after which we append to lst2
              for i, c in enumerate(cmd):
                if i == 0:
                  continue
                if c == 'then':
                  lst2 = cmd[i+1:]
                  break
                lst.append(c)
              
              # compress list to string
              s = ''.join(lst)
              s = s.replace('`', '"')

              # if string is true then run lst2
              try:
                if eval(s):
                  return self.command(lst2)
                else:
                  return 0
              except Exception as e:
                print(f'Breakpoint in if statement: {e}')
                return -1
            
            # ECHO COMMAND
            case CMD.ECHO:
              print(cmd[1], end='')

            # ECHOLN COMMAND
            case CMD.ECHOLN:
              print(cmd[1], end='\n')
            
            # USER COMMAND
            case CMD.USER:
              user_CMD(cmd, isRoot)
            
            # EXIT COMMAND
            case CMD.EXIT:
              os.system('cls')
              print('Shutting down . . .')
              time.sleep(1)
              exit(0)
            
            # DUMP COMMAND
            case CMD.DUMP:
              if len(cmd) == 3:
                if not isFileProtected(self.CWD + '/' + cmd[1]) or isRoot:
                  try:
                    f1 = open(cmd[1], 'rb')
                    f2 = open(cmd[2], 'wb')
                    f2.write(f1.read())
                    f1.close()
                    f2.close()
                    print('command completed')
                  except FileNotFoundError:
                    print('file not found')
                    return -1
                else:
                  print('File is protected')
                  return -5
                
              else:
                print('invalid number of arguments, expected 2, got ' + str(len(cmd) - 1))
                return -1 
                  

            # SETV COMMAND
            case CMD.SETV:
              if len(cmd) == 3:
                VARS[cmd[1]] = cmd[2]
              else:
                print(f'Invalid command, expected: 1 arg got: {len(cmd)-1}')
            
            # GETV COMMAND
            case CMD.GETV:
              if cmd[1] in VARS:
                LV = VARS[cmd[1]]
              else:
                print(f'Variable {cmd[1]} not found')
                return -1
            
            # DELV COMMAND
            case CMD.DELV:
              # pop the key from the dictionary
              if cmd[1] in VARS:
                VARS.pop(cmd[1])
              else:
                print('variable not found')
                return -1

            
        if cmd[0] not in CMD.CMD_LIST:
          print('invalid command')
          return -1

      except IndexError:
        pass

bp = BashProcesser()
while True:
    cmd = input(f'{CullPath(bp.GetCwd())} ~ $ ')
    cml = bp.ParseCmd(cmd)
    err = bp.command(cml)
    if err != 0 and err is not None:
        print(f'Shell Error {err} | {MapError(err)}')