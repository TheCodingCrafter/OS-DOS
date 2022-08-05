MAIN_DRIVE_PATH = './FILES'
USR_HOME = './FILES/usr'

class CMD:
    LS = 'ls' # List files
    CD = 'cd' # Change directory
    MKD = 'mkd' # Make directory
    RMD = 'rmd' # Remove directory
    MKF = 'mkf' # Make file
    RMF = 'rmf' # Remove file
    DUMP = 'dump' # Dump file X -> Y
    SUDO = 'sudo' # Run as root
    HELP = 'help' # Help
    EDIT = 'edit' # Edit file
    APT = 'apt' # Run apt
    DISKMGMT = 'diskmgmt' # Disk management
    WHOAMI = 'whoami' # Print username
    TOUCH = 'touch' # Get file size in bytes
    CLS = 'cls' # Clear screen
    EXECUTE = 'execute' # Execute script
    GETS = 'gets' # Get user input
    CAT = 'cat' # View file
    APPEND = 'append' # Append to file
    APPEND_TOP = 'append-top' # Append to file from top
    LOOP = 'loop' # Loop an command x times
    IF = 'if' # run cmd if condition is true
    ECHO = 'echo' # Print to screen
    ECHOLN = 'echoln' # Print to screen with newline
    USER = 'user' # user command
    EXIT = 'exit' # Exit program
    SETV = 'setv' # Set variable
    GETV = 'getv' # Get variable
    DELV = 'delv' # Delete variable


    CMD_LIST = [LS, CD, MKD, RMD, MKF, RMF, SUDO, HELP, EDIT, APT, DISKMGMT, WHOAMI, TOUCH, CLS, EXECUTE,
                GETS, CAT, APPEND, APPEND_TOP, LOOP, IF, ECHO, USER, EXIT, SETV, GETV, ECHOLN,
                DUMP, DELV]